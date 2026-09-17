"""Seleção temporal de parâmetros para priorizar trechos da rodovia.

O modelo não tenta prever a gravidade de um acidente que já ocorreu. Ele usa
apenas o histórico disponível antes de cada mês para ordenar os quilômetros
com maior severidade esperada no mês seguinte.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GridSearchCV

from context_features import enrich


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = BASE_DIR / "data" / "accidents"
DEFAULT_INMET_DIR = BASE_DIR.parent / "ProcessamentoParametros" / "weather-data"


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


def make_dataset(accidents: pd.DataFrame, external_dir: Path | None = None, inmet_dir: Path | None = DEFAULT_INMET_DIR) -> pd.DataFrame:
    """Cria uma linha por km/mês e variáveis calculadas somente do passado."""
    accidents["PERIODO"] = accidents["DATA"].dt.to_period("M")
    monthly = accidents.groupby(["PERIODO", "KM"], as_index=False).agg(
        acidentes=("SEVERIDADE", "size"), severidade=("SEVERIDADE", "sum")
    )
    periods = pd.period_range(monthly["PERIODO"].min(), monthly["PERIODO"].max(), freq="M")
    kms = range(int(monthly["KM"].min()), int(monthly["KM"].max()) + 1)
    panel = pd.MultiIndex.from_product([periods, kms], names=["PERIODO", "KM"]).to_frame(index=False)
    panel = panel.merge(monthly, on=["PERIODO", "KM"], how="left").fillna({"acidentes": 0, "severidade": 0})
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
    panel["ano"] = panel["PERIODO"].dt.year
    panel = panel.dropna().sort_values(["PERIODO", "KM"]).reset_index(drop=True)
    return enrich(panel, external_dir, inmet_dir)


def emergency_capture(y_true, y_pred, fraction: float = 0.10) -> float:
    """Fração da severidade real capturada ao inspecionar os 10% mais urgentes."""
    actual = pd.Series(y_true).clip(lower=0).reset_index(drop=True)
    if actual.sum() == 0:
        return 0.0
    selected = pd.Series(y_pred).nlargest(max(1, round(len(actual) * fraction))).index
    return float(actual.iloc[selected].sum() / actual.sum())


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


def run(data_dir: Path, output: Path, top_fraction: float, external_dir: Path | None = None, inmet_dir: Path | None = DEFAULT_INMET_DIR) -> dict:
    data = make_dataset(load_accidents(data_dir), external_dir, inmet_dir)
    excluded = {"PERIODO", "acidentes", "severidade"}
    feature_columns = [column for column in data.columns if column not in excluded and pd.api.types.is_numeric_dtype(data[column])]
    data[feature_columns] = data[feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    # O último ano é um teste final e nunca participa da escolha de parâmetros.
    last_year = int(data["ano"].max())
    train = data[data["ano"] < last_year].reset_index(drop=True)
    test = data[data["ano"] == last_year].reset_index(drop=True)
    if train.empty or test.empty:
        raise ValueError("É preciso ter pelo menos dois anos distintos de acidentes.")

    # Uma única execução evita diferenças de plataforma e funciona também em
    # ambientes restritos que não permitem processos filhos.
    model = ExtraTreesRegressor(random_state=42, n_jobs=1)
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
        scoring=lambda estimator, features, target: emergency_capture(target, estimator.predict(features), top_fraction),
        cv=temporal_splits(train),
        n_jobs=1,
        refit=True,
    )
    search.fit(train[feature_columns], train["severidade"])
    predictions = search.predict(test[feature_columns])
    ranked = test[["PERIODO", "KM", "severidade"]].copy()
    ranked["risco_previsto"] = predictions
    ranked = ranked.sort_values("risco_previsto", ascending=False)

    report = {
        "modelo": "ExtraTreesRegressor",
        "metrica_de_escolha": f"severidade real capturada no top {top_fraction:.0%} de km priorizados",
        "melhores_parametros": search.best_params_,
        "validacao_temporal": round(float(search.best_score_), 4),
        "teste_ano_final": last_year,
        "captura_no_teste": round(emergency_capture(test["severidade"], predictions, top_fraction), 4),
        "mae_no_teste": round(float(mean_absolute_error(test["severidade"], predictions)), 4),
        "variaveis": feature_columns,
        "alerta": "O ranking mede risco histórico. Antes de uso operacional, inclua exposição ao tráfego e valide com equipe de segurança viária.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    ranked.to_csv(output.with_name("ranking_km_previsto.csv"), index=False, encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Busca os melhores parâmetros para ordenar km emergenciais.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=BASE_DIR / "data" / "grid_search_report.json")
    parser.add_argument("--top-fraction", type=float, default=0.10)
    parser.add_argument("--external-dir", type=Path, help="Pasta opcional com traffic.csv, weather.csv, works.csv e infrastructure.csv")
    parser.add_argument("--inmet-dir", type=Path, default=DEFAULT_INMET_DIR, help="Pasta dos CSVs horários do INMET")
    args = parser.parse_args()
    if not 0 < args.top_fraction <= 1:
        parser.error("--top-fraction deve estar entre 0 e 1.")
    print(json.dumps(run(args.data_dir, args.output, args.top_fraction, args.external_dir, args.inmet_dir), ensure_ascii=False, indent=2))
