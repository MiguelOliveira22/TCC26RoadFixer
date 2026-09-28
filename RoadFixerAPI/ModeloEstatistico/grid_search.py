"""Seleção temporal de parâmetros para priorizar trechos da rodovia.

O modelo não tenta prever a gravidade de um acidente que já ocorreu. Ele usa
apenas o histórico disponível antes de cada mês para ordenar os quilômetros
com maior severidade esperada no mês seguinte.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GridSearchCV

try:  # Funciona como módulo e como script executado da pasta do projeto.
    from .context_features import enrich
except ImportError:  # pragma: no cover - caminho de execução por CLI
    from context_features import enrich


BASE_DIR = Path(__file__).resolve().parent
API_DIR = BASE_DIR.parent / "API" / "content" / "accident-history" / "risk"
DEFAULT_DATA_DIR = BASE_DIR.parent / "data" / "accidents" / "processed"
DEFAULT_EXTERNAL_DIR = BASE_DIR / "data_tau" / "external"
# Os caches em ``data/weather-data`` estão ligados a ocorrências e não formam
# uma série meteorológica contínua. Usá-los como INMET produziria vazamento.
DEFAULT_INMET_DIR: Path | None = None


def severity(row: pd.Series) -> float:
    """Custo de prevenção: mortes e feridos graves têm maior prioridade."""
    return (
        1 * row["VITIMA_LEVE"]
        + 2 * row["VITIMA_MODERADA"]
        + 5 * row["VITIMA_GRAVE"]
        + 13 * row["VITIMA_FATAL"]
    )


def load_accidents(data_dir: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(data_dir.glob("p*.csv")):
        data = pd.read_csv(path, encoding="utf-8")
        required = {"DATA", "RODOVIA", "KM", "VITIMA_LEVE", "VITIMA_MODERADA", "VITIMA_GRAVE", "VITIMA_FATAL"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(f"{path.name} não possui as colunas: {', '.join(sorted(missing))}")
        frames.append(data)
    if not frames:
        raise FileNotFoundError(f"Nenhum arquivo p*.csv encontrado em {data_dir}")

    data = pd.concat(frames, ignore_index=True)
    # O painel operacional é da rodovia principal. Registros de marginais e
    # acessos (SPM330*, SPA*/330 etc.) não têm a mesma exposição, geometria ou
    # quilometragem da SP-330 e não podem compartilhar a mesma linha do painel.
    road = data["RODOVIA"].astype(str).str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    data = data[road.eq("SP330")].copy()
    if data.empty:
        raise ValueError("Nenhum acidente da SP-330 foi encontrado nos arquivos processados.")
    data["DATA"] = pd.to_datetime(data["DATA"], errors="coerce")
    data["KM"] = pd.to_numeric(data["KM"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    victim_columns = ["VITIMA_LEVE", "VITIMA_MODERADA", "VITIMA_GRAVE", "VITIMA_FATAL"]
    data[victim_columns] = data[victim_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    data = data.dropna(subset=["DATA", "KM"]).copy()
    data["KM"] = data["KM"].round().astype(int)
    data["SEVERIDADE"] = data.apply(severity, axis=1)
    return data


def make_dataset(
    accidents: pd.DataFrame,
    external_dir: Path | None = None,
    inmet_dir: Path | None = DEFAULT_INMET_DIR,
    include_forecast_month: bool = False,
) -> pd.DataFrame:
    """Cria uma linha por km/mês; opcionalmente inclui o próximo mês sem alvo."""
    accidents["PERIODO"] = accidents["DATA"].dt.to_period("M")
    monthly = accidents.groupby(["PERIODO", "KM"], as_index=False).agg(
        acidentes=("SEVERIDADE", "size"), severidade=("SEVERIDADE", "sum")
    )
    last_observed_period = monthly["PERIODO"].max()
    end_period = last_observed_period + 1 if include_forecast_month else last_observed_period
    periods = pd.period_range(monthly["PERIODO"].min(), end_period, freq="M")
    kms = range(int(monthly["KM"].min()), int(monthly["KM"].max()) + 1)
    panel = pd.MultiIndex.from_product([periods, kms], names=["PERIODO", "KM"]).to_frame(index=False)
    panel = panel.merge(monthly, on=["PERIODO", "KM"], how="left")
    panel["alvo_observado"] = panel["PERIODO"] <= last_observed_period
    panel.loc[panel["alvo_observado"], ["acidentes", "severidade"]] = panel.loc[
        panel["alvo_observado"], ["acidentes", "severidade"]
    ].fillna(0)
    panel = panel.sort_values(["KM", "PERIODO"]).reset_index(drop=True)

    # shift(1) impede que o mês a ser previsto vaze para as variáveis.
    for months, name in ((1, "30d"), (3, "90d"), (12, "365d")):
        panel[f"acidentes_{name}"] = panel.groupby("KM")["acidentes"].transform(
            lambda values: values.shift(1).rolling(months, min_periods=1).sum()
        )
        panel[f"severidade_{name}"] = panel.groupby("KM")["severidade"].transform(
            lambda values: values.shift(1).rolling(months, min_periods=1).sum()
        )

    panel["mes"] = panel["PERIODO"].dt.month
    panel["mes_seno"] = __import__("numpy").sin(2 * __import__("numpy").pi * panel["mes"] / 12)
    panel["mes_cosseno"] = __import__("numpy").cos(2 * __import__("numpy").pi * panel["mes"] / 12)
    panel["ano"] = panel["PERIODO"].dt.year
    panel = panel.dropna(subset=["acidentes_30d", "severidade_30d"]).sort_values(["PERIODO", "KM"]).reset_index(drop=True)
    return enrich(panel, external_dir, inmet_dir)


def emergency_capture(y_true, y_pred, fraction: float = 0.10) -> float:
    """Fração da severidade real capturada ao inspecionar os 10% mais urgentes."""
    actual = pd.Series(y_true).clip(lower=0).reset_index(drop=True)
    predicted = pd.Series(y_pred).reset_index(drop=True)
    if actual.sum() == 0:
        return 0.0
    selected = predicted.nlargest(max(1, round(len(actual) * fraction))).index
    return float(actual.iloc[selected].sum() / actual.sum())


def monthly_emergency_capture(data: pd.DataFrame, prediction_column: str, fraction: float) -> float:
    """Média da captura mensal, alinhada à escala de decisão da operação."""
    captures = []
    for _, month in data.groupby("PERIODO"):
        if month["severidade"].sum() > 0:
            captures.append(emergency_capture(month["severidade"], month[prediction_column], fraction))
    return float(sum(captures) / len(captures)) if captures else 0.0


def temporal_splits(data: pd.DataFrame, folds: int = 3):
    months = sorted(data["PERIODO"].unique())
    if len(months) < folds + 2:
        raise ValueError("São necessários ao menos cinco meses de histórico para validar o modelo.")
    chunks = [chunk for chunk in __import__("numpy").array_split(months, folds + 1) if len(chunk)]
    splits = []
    for index in range(1, len(chunks)):
        train_months = set(month for chunk in chunks[:index] for month in chunk)
        test_months = set(chunks[index])
        train = data.index[data["PERIODO"].isin(train_months)].to_numpy()
        test = data.index[data["PERIODO"].isin(test_months)].to_numpy()
        if len(train) and len(test):
            splits.append((train, test))
    return splits


def _feature_columns(data: pd.DataFrame) -> list[str]:
    excluded = {"PERIODO", "acidentes", "severidade", "alvo_observado", "ano", "mes"}
    return [column for column in data.columns if column not in excluded and pd.api.types.is_numeric_dtype(data[column])]


def _carry_context_forward(data: pd.DataFrame) -> pd.DataFrame:
    """Imputa contexto somente com a última medição do próprio km, sem futuro."""
    contextual = [
        column for column in (
            "fluxo_total", "fluxo_pesados", "percentual_pesados", "chuva_mm", "vento_kmh",
            "visibilidade_km", "velocidade_media_kmh", "velocidade_livre_kmh", "indice_congestionamento",
        ) if column in data.columns
    ]
    if not contextual:
        return data
    result = data.sort_values(["KM", "PERIODO"]).copy()
    result[contextual] = result.groupby("KM")[contextual].ffill()
    return result.sort_index()


def _last_complete_year(data: pd.DataFrame) -> int:
    last_period = data.loc[data["alvo_observado"], "PERIODO"].max()
    return last_period.year if last_period.month == 12 else last_period.year - 1


def _risk_index(predictions: pd.Series) -> pd.Series:
    values = pd.Series(predictions).clip(lower=0)
    if values.nunique() <= 1:
        return pd.Series(0.0, index=values.index)
    return (values.rank(method="average", pct=True) * 10).round(3)


def _write_api_risk(forecast: pd.DataFrame, report: dict, path: Path) -> None:
    max_km = int(forecast["KM"].max())
    risk = [0.0] * (max_km + 1)
    for row in forecast.itertuples(index=False):
        risk[int(row.KM)] = float(row.indice_risco)
    payload = {
        "last_update": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "periodo_previsto": str(forecast["PERIODO"].iloc[0]),
        "metodo": "ExtraTrees - índice de priorização, não probabilidade",
        "risk": risk,
        "metricas": {
            "captura_mensal_validacao": report["validacao_temporal"],
            "captura_mensal_teste": report["captura_mensal_no_teste"],
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run(
    data_dir: Path,
    output: Path,
    top_fraction: float,
    external_dir: Path | None = DEFAULT_EXTERNAL_DIR,
    inmet_dir: Path | None = DEFAULT_INMET_DIR,
    api_risk_output: Path | None = API_DIR / "savedData.json",
) -> dict:
    accidents = load_accidents(data_dir)
    data = _carry_context_forward(make_dataset(accidents, external_dir, inmet_dir))
    feature_columns = _feature_columns(data)
    data[feature_columns] = data[feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    # O último ano completo é o teste final; o ano corrente parcial só entra
    # no refit final que emite a previsão operacional.
    last_year = _last_complete_year(data)
    train = data[(data["ano"] < last_year) & data["alvo_observado"]].reset_index(drop=True)
    test = data[(data["ano"] == last_year) & data["alvo_observado"]].reset_index(drop=True)
    if train.empty or test.empty:
        raise ValueError("É preciso ter pelo menos dois anos distintos de acidentes.")

    # Uma única execução evita diferenças de plataforma e funciona também em
    # ambientes restritos que não permitem processos filhos.
    model = ExtraTreesRegressor(random_state=42, n_jobs=1)

    def temporal_priority_score(estimator, features, target):
        validation = pd.DataFrame({
            "PERIODO": train.loc[features.index, "PERIODO"].to_numpy(),
            "severidade": target.to_numpy(),
            "previsao": estimator.predict(features),
        })
        return monthly_emergency_capture(validation, "previsao", top_fraction)

    search = GridSearchCV(
        estimator=model,
        param_grid={
            # Grade intencionalmente compacta para viabilizar a atualização
            # diária; pode ser ampliada em uma rodada de pesquisa offline.
            "n_estimators": [100],
            "max_depth": [None, 8],
            "min_samples_leaf": [3, 8],
            "max_features": [0.7, 1.0],
        },
        scoring=temporal_priority_score,
        cv=temporal_splits(train),
        n_jobs=1,
        refit=True,
    )
    search.fit(train[feature_columns], train["severidade"])
    predictions = search.predict(test[feature_columns])
    ranked = test[["PERIODO", "KM", "severidade"]].copy()
    ranked["risco_previsto"] = predictions
    ranked = ranked.sort_values("risco_previsto", ascending=False)

    observed = data[data["alvo_observado"]].copy()
    final_model = ExtraTreesRegressor(random_state=42, n_jobs=1, **search.best_params_)
    final_model.fit(observed[feature_columns], observed["severidade"])
    future = _carry_context_forward(make_dataset(accidents, external_dir, inmet_dir, include_forecast_month=True))
    future[feature_columns] = future[feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    forecast = future[~future["alvo_observado"]][["PERIODO", "KM"]].copy()
    forecast["severidade_prevista"] = final_model.predict(future.loc[~future["alvo_observado"], feature_columns]).clip(min=0)
    forecast["indice_risco"] = _risk_index(forecast["severidade_prevista"])
    forecast = forecast.sort_values("indice_risco", ascending=False)

    report = {
        "modelo": "ExtraTreesRegressor",
        "metrica_de_escolha": f"média mensal da severidade real capturada no top {top_fraction:.0%} de km priorizados",
        "melhores_parametros": search.best_params_,
        "validacao_temporal": round(float(search.best_score_), 4),
        "teste_ano_final": last_year,
        "captura_mensal_no_teste": round(monthly_emergency_capture(ranked, "risco_previsto", top_fraction), 4),
        "captura_global_no_teste": round(emergency_capture(test["severidade"], predictions, top_fraction), 4),
        "mae_no_teste": round(float(mean_absolute_error(test["severidade"], predictions)), 4),
        "variaveis": feature_columns,
        "periodo_previsto": str(forecast["PERIODO"].iloc[0]),
        "importancia_das_variaveis": dict(sorted(zip(feature_columns, final_model.feature_importances_), key=lambda item: item[1], reverse=True)),
        "alerta": "Índice de priorização para triagem humana; não é probabilidade de acidente nem substitui auditoria de segurança viária.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    ranked.to_csv(output.with_name("ranking_km_previsto.csv"), index=False, encoding="utf-8")
    forecast.to_csv(output.with_name("ranking_km_proximo_mes.csv"), index=False, encoding="utf-8")
    if api_risk_output:
        _write_api_risk(forecast, report, api_risk_output)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Busca os melhores parâmetros para ordenar km emergenciais.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=BASE_DIR / "data_tau" / "grid_search_report.json")
    parser.add_argument("--top-fraction", type=float, default=0.10)
    parser.add_argument("--external-dir", type=Path, default=DEFAULT_EXTERNAL_DIR, help="Pasta opcional com traffic.csv, weather.csv, works.csv e infrastructure.csv")
    parser.add_argument("--inmet-dir", type=Path, default=DEFAULT_INMET_DIR, help="Pasta dos CSVs horários do INMET")
    args = parser.parse_args()
    if not 0 < args.top_fraction <= 1:
        parser.error("--top-fraction deve estar entre 0 e 1.")
    print(json.dumps(run(args.data_dir, args.output, args.top_fraction, args.external_dir, args.inmet_dir), ensure_ascii=False, indent=2))
