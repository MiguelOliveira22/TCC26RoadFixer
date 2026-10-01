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
import numpy as np
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
# Os arquivos de clima do processamento são cache de ocorrências e não seguem
# o contrato mensal do INMET. Só use INMET quando uma fonte própria for passada.
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
        required = {"DATA", "KM", "VITIMA_LEVE", "VITIMA_MODERADA", "VITIMA_GRAVE", "VITIMA_FATAL"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(f"{path.name} não possui as colunas: {', '.join(sorted(missing))}")
        frames.append(data)
    if not frames:
        raise FileNotFoundError(f"Nenhum arquivo p*.csv encontrado em {data_dir}")

    data = pd.concat(frames, ignore_index=True)
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
    """Cria uma linha por km/mês; opcionalmente acrescenta o próximo mês sem alvo."""
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
    # A primeira linha de cada km não tem histórico para formar as defasagens.
    panel = panel.dropna(subset=["acidentes_30d", "severidade_30d"]).sort_values(["PERIODO", "KM"]).reset_index(drop=True)
    panel = enrich(panel, external_dir, inmet_dir)
    if "exposicao_veiculo_km" not in panel:
        raise ValueError("Não há dados de tráfego para calcular exposição em veículos-km.")
    exposure = pd.to_numeric(panel["exposicao_veiculo_km"], errors="coerce")
    panel["severidade_por_milhao_vkm"] = (panel["severidade"] / (exposure / 1_000_000)).where(
        panel["alvo_observado"] & exposure.gt(0)
    )

    # Baselines sem vazamento: cada taxa usa apenas severidade e exposição
    # observadas antes do mês previsto.
    ordered = panel.sort_values(["KM", "PERIODO"]).copy()
    valid = ordered["alvo_observado"] & exposure.loc[ordered.index].gt(0)
    severity_observed = ordered["severidade"].where(valid)
    exposure_observed = exposure.loc[ordered.index].where(valid)
    grouped_severity = severity_observed.groupby(ordered["KM"], sort=False)
    grouped_exposure = exposure_observed.groupby(ordered["KM"], sort=False)
    severity_12m = grouped_severity.transform(lambda values: values.shift(1).rolling(12, min_periods=1).sum())
    exposure_12m = grouped_exposure.transform(lambda values: values.shift(1).rolling(12, min_periods=1).sum())
    months_12m = valid.astype(int).groupby(ordered["KM"], sort=False).transform(
        lambda values: values.shift(1).rolling(12, min_periods=1).sum()
    )
    severity_all = grouped_severity.transform(lambda values: values.shift(1).expanding(min_periods=1).sum())
    exposure_all = grouped_exposure.transform(lambda values: values.shift(1).expanding(min_periods=1).sum())
    ordered["taxa_historica_365d"] = (severity_12m / (exposure_12m / 1_000_000)).where(months_12m >= 10)
    ordered["taxa_media_historica"] = severity_all / (exposure_all / 1_000_000)
    panel["taxa_historica_365d"] = ordered["taxa_historica_365d"].reindex(panel.index)
    panel["taxa_media_historica"] = ordered["taxa_media_historica"].reindex(panel.index)
    panel["meses_com_exposicao_365d"] = months_12m.reindex(panel.index)
    panel["meses_com_acidente_365d"] = ordered.groupby("KM", sort=False)["acidentes"].transform(
        lambda values: values.shift(1).rolling(12, min_periods=1).apply(lambda window: (window > 0).sum(), raw=True)
    ).reindex(panel.index)
    return panel


def emergency_capture(y_true, y_pred, fraction: float = 0.10) -> float:
    """Fração da severidade real capturada ao inspecionar os 10% mais urgentes."""
    actual = pd.Series(y_true).clip(lower=0).reset_index(drop=True)
    predicted = pd.Series(y_pred).reset_index(drop=True)
    if actual.sum() == 0:
        return 0.0
    selected = predicted.nlargest(max(1, round(len(actual) * fraction))).index
    return float(actual.iloc[selected].sum() / actual.sum())


def monthly_emergency_capture(
    data: pd.DataFrame,
    prediction_column: str,
    fraction: float,
    actual_column: str = "severidade_por_milhao_vkm",
) -> float:
    """Média mensal da taxa observada capturada nos trechos priorizados."""
    captures = []
    for _, month in data.groupby("PERIODO"):
        if month[actual_column].sum() > 0:
            captures.append(emergency_capture(month[actual_column], month[prediction_column], fraction))
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
    # O ano não generaliza bem em árvores para um ano ainda não observado; a
    # sazonalidade fica representada por seno/cosseno do mês.
    excluded = {
        "PERIODO", "acidentes", "severidade", "alvo_observado", "ano", "mes",
        "exposicao_veiculo_km", "severidade_por_milhao_vkm", "mes_origem_fluxo",
    }
    return [column for column in data.columns if column not in excluded and pd.api.types.is_numeric_dtype(data[column])]


def _carry_context_forward(data: pd.DataFrame) -> pd.DataFrame:
    """Imputa somente com a última medição disponível do próprio km.

    A ARTESP pode publicar tráfego e clima com atraso. Preencher lacunas com a
    medição futura seria vazamento; ``ffill`` ordenado por km/período mantém a
    última informação que uma execução operacional realmente teria.
    """
    contextual = [
        column
        for column in (
            "fluxo_total", "fluxo_pesados", "percentual_pesados", "chuva_mm",
            "vento_kmh", "visibilidade_km", "velocidade_media_kmh",
            "velocidade_livre_kmh", "indice_congestionamento", "mes_origem_fluxo",
        )
        if column in data.columns
    ]
    if not contextual:
        return data
    result = data.sort_values(["KM", "PERIODO"]).copy()
    result[contextual] = result.groupby("KM")[contextual].ffill()
    if "mes_origem_fluxo" in result:
        result["meses_desde_fluxo"] = [
            max(0, period.ordinal - int(origin)) if pd.notna(origin) else np.nan
            for period, origin in zip(result["PERIODO"], result["mes_origem_fluxo"])
        ]
        result = result.drop(columns="mes_origem_fluxo")
    return result.sort_index()


def _last_complete_year(data: pd.DataFrame) -> int:
    last_period = data.loc[data["alvo_observado"], "PERIODO"].max()
    return last_period.year if last_period.month == 12 else last_period.year - 1


def _risk_index(predictions: pd.Series) -> pd.Series:
    """Converte severidade prevista em índice de priorização estável de 0 a 10."""
    values = pd.Series(predictions).clip(lower=0)
    if values.nunique() <= 1:
        return pd.Series(0.0, index=values.index)
    return (values.rank(method="average", pct=True) * 10).round(3)


def _baseline_scores(data: pd.DataFrame, splits: list[tuple[np.ndarray, np.ndarray]], fraction: float) -> dict:
    baselines = ("taxa_historica_365d", "taxa_media_historica")
    scores = {name: [] for name in baselines}
    for _, validation_indices in splits:
        validation = data.loc[validation_indices].copy()
        for name in baselines:
            prediction = validation[name].fillna(0)
            scored = validation.assign(_baseline=prediction)
            scores[name].append(monthly_emergency_capture(scored, "_baseline", fraction))
    return {name: float(np.mean(values)) if values else 0.0 for name, values in scores.items()}


def _evidence(row: pd.Series, traffic_fresh_months: int = 2) -> tuple[list[str], str]:
    """Resume sinais observados; não atribui causalidade a nenhum fator."""
    evidence = []
    accidents = float(row.get("acidentes_365d", 0) or 0)
    severity = float(row.get("severidade_30d", 0) or 0)
    if accidents > 0:
        evidence.append(f"{int(accidents)} acidente(s) registrados nos 365 dias anteriores")
    if severity > 0:
        evidence.append(f"severidade ponderada recente de {severity:.1f} nos 30 dias anteriores")
    heavy_share = row.get("percentual_pesados")
    if pd.notna(heavy_share) and 0 <= float(heavy_share) <= 1:
        evidence.append(f"veículos pesados representam {float(heavy_share) * 100:.1f}% do fluxo conhecido")
    flow_age = row.get("meses_desde_fluxo")
    flow = row.get("fluxo_total")
    fresh = (
        pd.notna(flow_age)
        and 0 <= float(flow_age) <= traffic_fresh_months
        and pd.notna(flow)
        and float(flow) >= 0
    )
    if fresh:
        evidence.append(f"fluxo mensal estimado em {float(flow):,.0f} passagens, com contagem recente")
    elif pd.notna(flow_age) and float(flow_age) >= 0:
        evidence.append(f"contagem de tráfego defasada em {int(flow_age)} mês(es)")
    else:
        evidence.append("sem contagem de tráfego disponível")
    for column, label in (
        ("acessos_nao_autorizados", "acesso cadastrado como não autorizado"),
        ("acessos_nao_conformes", "acesso cadastrado como não conforme"),
        ("acessos_conservacao_ruim", "acesso cadastrado em conservação ruim"),
    ):
        if float(row.get(column, 0) or 0) > 0:
            evidence.append(label)
    event_months = int(float(row.get("meses_com_acidente_365d", 0) or 0))
    confidence = "baixa" if event_months < 2 or not fresh else ("moderada" if event_months < 6 else "maior")
    return evidence or ["sem sinal histórico destacado"], confidence


def _write_api_risk(forecast: pd.DataFrame, report: dict, path: Path) -> None:
    max_km = int(forecast["KM"].max())
    risk = [0.0] * (max_km + 1)
    for row in forecast.itertuples(index=False):
        risk[int(row.KM)] = float(row.indice_risco)
    payload = {
        "last_update": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "periodo_previsto": str(forecast["PERIODO"].iloc[0]),
        "metodo": "ExtraTrees - taxa de severidade por milhão de veículos-km; índice relativo, não probabilidade",
        "unidade": "severidade ponderada por milhão de veículos-km",
        "exposicao": "fluxo somado nos dois sentidos em células de 1 km; quilometragens agregadas",
        "faixa_previsao": report["faixa_previsao"],
        "qualidade_dados": report["qualidade_dados"],
        "risk": risk,
        "trechos": [
            {
                "km": int(row.KM),
                "indice_risco": float(row.indice_risco),
                "taxa_prevista": float(row.taxa_prevista),
                "limite_inferior": float(row.limite_inferior),
                "limite_superior": float(row.limite_superior),
                "acidentes_365d": int(row.acidentes_365d),
                "meses_com_acidente_365d": int(row.meses_com_acidente_365d),
                "meses_desde_fluxo": int(row.meses_desde_fluxo) if pd.notna(row.meses_desde_fluxo) and row.meses_desde_fluxo >= 0 else None,
                "confiabilidade_dados": row.confiabilidade_dados,
                "evidencias": row.evidencias,
            }
            for row in forecast.itertuples(index=False)
        ],
        "metricas": {
            "captura_mensal_validacao": report["validacao_temporal"],
            "captura_mensal_teste": report["captura_mensal_no_teste"],
            "baselines": report["baselines"],
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
    data = make_dataset(accidents, external_dir, inmet_dir)
    data = _carry_context_forward(data)
    feature_columns = _feature_columns(data)
    data[feature_columns] = data[feature_columns].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(-1)
    # O último ano completo é o teste final. Um ano corrente parcial não deve
    # parecer um teste anual nem contaminar a escolha de hiperparâmetros.
    last_year = _last_complete_year(data)
    eligible = data["alvo_observado"] & data["severidade_por_milhao_vkm"].notna()
    train = data[(data["ano"] < last_year) & eligible].reset_index(drop=True)
    test = data[(data["ano"] == last_year) & eligible].reset_index(drop=True)
    if train.empty or test.empty:
        raise ValueError("É preciso ter pelo menos dois anos distintos de acidentes.")

    # Uma única execução evita diferenças de plataforma e funciona também em
    # ambientes restritos que não permitem processos filhos.
    model = ExtraTreesRegressor(random_state=42, n_jobs=1)

    def temporal_priority_score(estimator, features, target):
        validation = pd.DataFrame(
            {
                "PERIODO": train.loc[features.index, "PERIODO"].to_numpy(),
                "severidade_por_milhao_vkm": target.to_numpy(),
                "previsao": estimator.predict(features),
            }
        )
        return monthly_emergency_capture(validation, "previsao", top_fraction)

    splits = temporal_splits(train)
    baseline_validation = _baseline_scores(train, splits, top_fraction)
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
        cv=splits,
        n_jobs=1,
        refit=True,
    )
    # PERIODO serve apenas para separar as dobras temporais; não entra no modelo.
    search.fit(train[feature_columns], train["severidade_por_milhao_vkm"])
    predictions = search.predict(test[feature_columns])
    ranked = test[["PERIODO", "KM", "severidade", "severidade_por_milhao_vkm"]].copy()
    ranked["risco_previsto"] = predictions
    ranked = ranked.sort_values("risco_previsto", ascending=False)
    baseline_test = {
        name: monthly_emergency_capture(
            test.assign(_baseline=test[name].fillna(0)), "_baseline", top_fraction
        )
        for name in ("taxa_historica_365d", "taxa_media_historica")
    }
    residual_q90 = float(np.quantile(np.abs(test["severidade_por_milhao_vkm"].to_numpy() - predictions), 0.90))

    # Depois do teste imutável, refaz o modelo com toda a história disponível
    # para emitir a previsão do próximo mês.
    observed = data[eligible].copy()
    final_model = ExtraTreesRegressor(random_state=42, n_jobs=1, **search.best_params_)
    final_model.fit(observed[feature_columns], observed["severidade_por_milhao_vkm"])
    future = make_dataset(accidents, external_dir, inmet_dir, include_forecast_month=True)
    future = _carry_context_forward(future)
    future[feature_columns] = future[feature_columns].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(-1)
    forecast = future[~future["alvo_observado"]][["PERIODO", "KM"]].copy()
    future_features = future.loc[~future["alvo_observado"], feature_columns]
    # As árvores internas do ExtraTrees são treinadas sem nomes de colunas;
    # passar um array aqui evita um aviso repetido por árvore no pipeline diário.
    tree_predictions = np.column_stack([tree.predict(future_features.to_numpy()) for tree in final_model.estimators_])
    forecast["taxa_prevista"] = tree_predictions.mean(axis=1).clip(min=0)
    forecast["limite_inferior"] = np.maximum(0, forecast["taxa_prevista"] - residual_q90)
    forecast["limite_superior"] = forecast["taxa_prevista"] + residual_q90
    forecast["indice_risco"] = _risk_index(forecast["taxa_prevista"])
    evidence_rows = future.loc[~future["alvo_observado"]].copy()
    evidence = evidence_rows.apply(_evidence, axis=1)
    forecast["evidencias"] = [item[0] for item in evidence]
    forecast["confiabilidade_dados"] = [item[1] for item in evidence]
    for column in ("acidentes_365d", "meses_com_acidente_365d", "meses_desde_fluxo"):
        if column in evidence_rows:
            forecast[column] = evidence_rows[column].to_numpy()
        else:
            forecast[column] = 0
    forecast = forecast.sort_values("indice_risco", ascending=False)

    all_test_rows = data[(data["ano"] == last_year) & data["alvo_observado"]]
    test_exposure_coverage = float(
        all_test_rows["exposicao_veiculo_km"].notna().mean() if len(all_test_rows) else 0.0
    )
    recent_flow = forecast["meses_desde_fluxo"].notna() & forecast["meses_desde_fluxo"].between(0, 2)
    quality = {
        "trechos_previstos": int(len(forecast)),
        "trechos_com_fluxo_de_ate_2_meses": int(recent_flow.sum()),
        "cobertura_fluxo_recente": round(float(recent_flow.mean()) if len(forecast) else 0.0, 4),
        "cobertura_exposicao_no_teste": round(test_exposure_coverage, 4),
        "anos_teste": int(last_year),
        "sentidos_agregados": True,
        "extensao_celula_km": 1,
    }

    report = {
        "modelo": "ExtraTreesRegressor",
        "metrica_de_escolha": f"média mensal da taxa de severidade por veículo-km capturada no top {top_fraction:.0%} de km",
        "melhores_parametros": search.best_params_,
        "validacao_temporal": round(float(search.best_score_), 4),
        "baselines": {
            "taxa_historica_365d": {
                "validacao_temporal": round(baseline_validation["taxa_historica_365d"], 4),
                "teste_ano_final": round(baseline_test["taxa_historica_365d"], 4),
            },
            "taxa_media_historica": {
                "validacao_temporal": round(baseline_validation["taxa_media_historica"], 4),
                "teste_ano_final": round(baseline_test["taxa_media_historica"], 4),
            },
        },
        "teste_ano_final": last_year,
        "captura_mensal_no_teste": round(monthly_emergency_capture(ranked, "risco_previsto", top_fraction), 4),
        "mae_taxa_por_milhao_vkm": round(float(mean_absolute_error(test["severidade_por_milhao_vkm"], predictions)), 4),
        "variaveis": feature_columns,
        "periodo_previsto": str(forecast["PERIODO"].iloc[0]),
        "unidade_alvo": "severidade ponderada por milhão de veículos-km",
        "faixa_previsao": {
            "metodo": "previsão ± percentil 90 dos erros absolutos no último ano de teste",
            "calibracao_ano": int(last_year),
            "quantil_erro_absoluto": round(residual_q90, 4),
            "aviso": "Faixa de referência temporal; não é intervalo de confiança calibrado para mudança de distribuição.",
        },
        "qualidade_dados": quality,
        "importancia_das_variaveis": dict(sorted(zip(feature_columns, final_model.feature_importances_), key=lambda item: item[1], reverse=True)),
        "alerta": "Índice de priorização para triagem humana; não é probabilidade nem prova causal. Exposição soma os dois sentidos em células de 1 km.",
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
