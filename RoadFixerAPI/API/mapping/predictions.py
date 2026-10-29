from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
from threading import RLock
from typing import Any

from fastapi import FastAPI, HTTPException, Query
import joblib
import numpy as np
import pandas as pd


ROADFIXER_API_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACTS_DIR = ROADFIXER_API_DIR / "ModeloEstatistico" / "artifacts"
DEFAULT_TRAFFIC_MODEL_PATH = DEFAULT_ARTIFACTS_DIR / "sarimax_volume_trafego.joblib"
DEFAULT_ACCIDENT_MODEL_PATH = DEFAULT_ARTIFACTS_DIR / "arimax_volume_acidentes.joblib"
DEFAULT_DATABASE_DIR = ROADFIXER_API_DIR / "Database" / "Processed"
DEFAULT_TRAFFIC_DATA_PATH = DEFAULT_DATABASE_DIR / "VolumeDiario.csv"
DEFAULT_ACCIDENT_DATA_PATH = DEFAULT_DATABASE_DIR / "Acidentes.csv"
TRAFFIC_COLUMNS = ["QTD_MOTO", "QTD_PASSEIO", "QTD_COMERCIAL"]


class ForecastModelError(RuntimeError):
    """Erro de carregamento ou incompatibilidade dos modelos de previsão."""


def _model_path(environment_name: str, default: Path) -> Path:
    configured = os.getenv(environment_name)
    return Path(configured).expanduser().resolve() if configured else default.resolve()


def _date_string(value: Any) -> str:
    return pd.Timestamp(value).date().isoformat()


def _json_number(value: Any) -> float | int | None:
    if value is None or pd.isna(value):
        return None
    number = float(value)
    return int(number) if number.is_integer() else number


def _json_mapping(values: dict[str, Any] | None) -> dict[str, float | int | None]:
    return {key: _json_number(value) for key, value in (values or {}).items()}


def _restore_scale(values: Any) -> np.ndarray:
    return np.clip(np.expm1(np.asarray(values, dtype=float)), a_min=0, a_max=None)


class JoblibForecastService:
    """Carrega os modelos treinados e produz o encadeamento SARIMAX -> ARIMAX."""

    def __init__(
        self,
        traffic_model_path: Path | None = None,
        accident_model_path: Path | None = None,
        traffic_data_path: Path | None = None,
        accident_data_path: Path | None = None,
    ) -> None:
        self.traffic_model_path = traffic_model_path or _model_path(
            "ROADFIXER_TRAFFIC_MODEL_PATH", DEFAULT_TRAFFIC_MODEL_PATH
        )
        self.accident_model_path = accident_model_path or _model_path(
            "ROADFIXER_ACCIDENT_MODEL_PATH", DEFAULT_ACCIDENT_MODEL_PATH
        )
        self.traffic_data_path = traffic_data_path or _model_path(
            "ROADFIXER_TRAFFIC_DATA_PATH", DEFAULT_TRAFFIC_DATA_PATH
        )
        self.accident_data_path = accident_data_path or _model_path(
            "ROADFIXER_ACCIDENT_DATA_PATH", DEFAULT_ACCIDENT_DATA_PATH
        )
        self._traffic_bundle: dict[str, Any] | None = None
        self._accident_bundle: dict[str, Any] | None = None
        self._history: pd.DataFrame | None = None
        self._loaded_at: datetime | None = None
        self._last_error: str | None = None
        self._lock = RLock()

    @property
    def loaded(self) -> bool:
        return self._traffic_bundle is not None and self._accident_bundle is not None

    def load(self) -> None:
        with self._lock:
            try:
                missing = [
                    path
                    for path in [
                        self.traffic_model_path,
                        self.accident_model_path,
                        self.traffic_data_path,
                        self.accident_data_path,
                    ]
                    if not path.is_file()
                ]
                if missing:
                    paths = ", ".join(str(path) for path in missing)
                    raise ForecastModelError(
                        "Artefatos Joblib não encontrados: "
                        f"{paths}. Execute volume_trafego.ipynb e volume_acidente.ipynb."
                    )

                traffic_bundle = joblib.load(self.traffic_model_path)
                accident_bundle = joblib.load(self.accident_model_path)
                self._validate_bundles(traffic_bundle, accident_bundle)
                history = self._load_history(
                    self.traffic_data_path,
                    self.accident_data_path,
                    pd.Timestamp(traffic_bundle["ultima_data_treino"]),
                )

                self._traffic_bundle = traffic_bundle
                self._accident_bundle = accident_bundle
                self._history = history
                self._loaded_at = datetime.now(timezone.utc)
                self._last_error = None
            except Exception as error:
                self._traffic_bundle = None
                self._accident_bundle = None
                self._history = None
                self._last_error = str(error)
                if isinstance(error, ForecastModelError):
                    raise
                raise ForecastModelError(
                    f"Não foi possível carregar os modelos Joblib: {error}"
                ) from error

    @staticmethod
    def _validate_bundles(
        traffic_bundle: dict[str, Any], accident_bundle: dict[str, Any]
    ) -> None:
        traffic_required = {
            "modelo",
            "ordem",
            "ordem_sazonal",
            "pontos_referencia",
            "pontos_futuros_assumidos",
            "data_referencia",
            "ultima_data_treino",
        }
        accident_required = {
            "modelo",
            "ordem",
            "media_volume_log",
            "desvio_volume_log",
            "data_referencia",
            "ultima_data_treino",
        }
        missing_traffic = sorted(traffic_required - set(traffic_bundle))
        missing_accident = sorted(accident_required - set(accident_bundle))
        if missing_traffic or missing_accident:
            raise ForecastModelError(
                "Artefatos incompatíveis. "
                f"Campos ausentes no SARIMAX: {missing_traffic}; "
                f"campos ausentes no ARIMAX: {missing_accident}."
            )

        traffic_last_date = pd.Timestamp(traffic_bundle["ultima_data_treino"])
        accident_last_date = pd.Timestamp(accident_bundle["ultima_data_treino"])
        if traffic_last_date != accident_last_date:
            raise ForecastModelError(
                "Os modelos não usam a mesma data final de treinamento: "
                f"SARIMAX={traffic_last_date.date()} e ARIMAX={accident_last_date.date()}."
            )

        if float(traffic_bundle["pontos_referencia"]) <= 0:
            raise ForecastModelError("pontos_referencia do SARIMAX precisa ser positivo.")
        if float(accident_bundle["desvio_volume_log"]) <= 0:
            raise ForecastModelError("desvio_volume_log do ARIMAX precisa ser positivo.")

    @staticmethod
    def _load_history(
        traffic_path: Path,
        accident_path: Path,
        last_training_date: pd.Timestamp,
    ) -> pd.DataFrame:
        try:
            traffic = pd.read_csv(
                traffic_path,
                usecols=["DATA", *TRAFFIC_COLUMNS],
                low_memory=False,
            )
            accidents = pd.read_csv(
                accident_path,
                usecols=["DATA"],
                low_memory=False,
            )
        except (OSError, ValueError) as error:
            raise ForecastModelError(
                f"Não foi possível ler o histórico diário dos CSVs: {error}"
            ) from error

        traffic["DATA"] = pd.to_datetime(
            traffic["DATA"], format="mixed", errors="coerce"
        ).dt.normalize()
        for column in TRAFFIC_COLUMNS:
            traffic[column] = pd.to_numeric(traffic[column], errors="coerce")
        traffic = traffic.dropna(subset=["DATA", *TRAFFIC_COLUMNS])
        traffic["VOLUME_TOTAL"] = traffic[TRAFFIC_COLUMNS].sum(axis=1)
        daily_traffic = traffic.groupby("DATA")["VOLUME_TOTAL"].sum().sort_index()

        accidents["DATA"] = pd.to_datetime(
            accidents["DATA"], format="mixed", errors="coerce"
        ).dt.normalize()
        daily_accidents = (
            accidents.dropna(subset=["DATA"])
            .groupby("DATA")
            .size()
            .rename("ACIDENTES")
            .sort_index()
        )

        history = pd.concat(
            [daily_traffic.rename("VOLUME_TRAFEGO"), daily_accidents], axis=1
        ).sort_index()
        history = history.loc[history.index <= last_training_date]
        history["ACIDENTES"] = history["ACIDENTES"].fillna(0)
        history = history.dropna(subset=["VOLUME_TRAFEGO"])

        if history.empty or history.index.max() != last_training_date:
            last_history_date = history.index.max().date() if not history.empty else None
            raise ForecastModelError(
                "O histórico agregado não alcança a data final do treinamento: "
                f"histórico={last_history_date}, modelo={last_training_date.date()}."
            )

        return history

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "carregado": self.loaded,
                "carregado_em": self._loaded_at.isoformat() if self._loaded_at else None,
                "erro": self._last_error,
                "artefatos": {
                    "sarimax_trafego": {
                        "caminho": str(self.traffic_model_path),
                        "existe": self.traffic_model_path.is_file(),
                    },
                    "arimax_acidentes": {
                        "caminho": str(self.accident_model_path),
                        "existe": self.accident_model_path.is_file(),
                    },
                },
                "fontes_historicas": {
                    "trafego": str(self.traffic_data_path),
                    "acidentes": str(self.accident_data_path),
                    "carregadas": self._history is not None,
                },
            }

    def forecast(self, days: int = 30, history_days: int = 30) -> dict[str, Any]:
        if not 1 <= days <= 30:
            raise ForecastModelError("O horizonte deve estar entre 1 e 30 dias.")
        if not 1 <= history_days <= 365:
            raise ForecastModelError("O histórico deve estar entre 1 e 365 dias.")

        with self._lock:
            if not self.loaded:
                detail = self._last_error or "Modelos ainda não carregados."
                raise ForecastModelError(detail)

            traffic_bundle = self._traffic_bundle
            accident_bundle = self._accident_bundle
            assert traffic_bundle is not None
            assert accident_bundle is not None
            assert self._history is not None

            history = self._history.tail(history_days)
            historical_values = [
                {
                    "data": date.date().isoformat(),
                    "volume_trafego": {"observado": int(round(row.VOLUME_TRAFEGO))},
                    "acidentes": {"observado": int(row.ACIDENTES)},
                }
                for date, row in history.iterrows()
            ]

            index, traffic_mean, traffic_lower, traffic_upper = self._forecast_traffic(
                traffic_bundle, days
            )
            accident_mean, accident_lower, accident_upper = self._forecast_accidents(
                accident_bundle, index, traffic_mean
            )

            traffic_rounded = np.rint(traffic_mean).astype(np.int64)
            traffic_lower_rounded = np.rint(traffic_lower).astype(np.int64)
            traffic_upper_rounded = np.rint(traffic_upper).astype(np.int64)
            accident_rounded = np.rint(accident_mean).astype(np.int64)
            accident_lower_rounded = np.floor(accident_lower).astype(np.int64)
            accident_upper_rounded = np.ceil(accident_upper).astype(np.int64)

            forecasts = []
            for position, date in enumerate(index):
                forecasts.append(
                    {
                        "data": date.date().isoformat(),
                        "volume_trafego": {
                            "previsao": int(traffic_rounded[position]),
                            "limite_inferior_95": int(traffic_lower_rounded[position]),
                            "limite_superior_95": int(traffic_upper_rounded[position]),
                        },
                        "acidentes": {
                            "previsao": int(accident_rounded[position]),
                            "limite_inferior_95": int(accident_lower_rounded[position]),
                            "limite_superior_95": int(accident_upper_rounded[position]),
                        },
                    }
                )

            traffic_peak = int(np.argmax(traffic_mean))
            accident_peak = int(np.argmax(accident_mean))
            return {
                "gerado_em": datetime.now(timezone.utc).isoformat(),
                "periodo": {
                    "inicio": index.min().date().isoformat(),
                    "fim": index.max().date().isoformat(),
                    "dias": days,
                },
                "periodo_historico": {
                    "inicio": history.index.min().date().isoformat(),
                    "fim": history.index.max().date().isoformat(),
                    "dias": len(history),
                },
                "resumo": {
                    "volume_medio_diario": int(np.rint(traffic_mean.mean())),
                    "volume_maximo_diario": int(traffic_rounded[traffic_peak]),
                    "data_maior_volume": index[traffic_peak].date().isoformat(),
                    "acidentes_previstos_total": int(np.rint(accident_mean.sum())),
                    "acidentes_media_diaria": round(float(accident_mean.mean()), 2),
                    "acidentes_maximo_diario": int(accident_rounded[accident_peak]),
                    "data_maior_previsao_acidentes": index[
                        accident_peak
                    ].date().isoformat(),
                },
                "modelos": {
                    "trafego": {
                        "tipo": "SARIMAX",
                        "ordem": list(traffic_bundle["ordem"]),
                        "ordem_sazonal": list(traffic_bundle["ordem_sazonal"]),
                        "ultima_data_treino": _date_string(
                            traffic_bundle["ultima_data_treino"]
                        ),
                        "metricas_validacao": _json_mapping(
                            traffic_bundle.get("metricas_validacao")
                        ),
                    },
                    "acidentes": {
                        "tipo": "ARIMAX",
                        "ordem": list(accident_bundle["ordem"]),
                        "ultima_data_treino": _date_string(
                            accident_bundle["ultima_data_treino"]
                        ),
                        "metricas_validacao": _json_mapping(
                            accident_bundle.get("metricas_validacao")
                        ),
                        "metricas_encadeadas": _json_mapping(
                            accident_bundle.get("metricas_encadeadas")
                        ),
                    },
                },
                "aviso": (
                    "Estimativas agregadas para planejamento. O intervalo de acidentes "
                    "é condicional à previsão central de tráfego e não representa "
                    "probabilidade de ocorrência em um local específico."
                ),
                "historico": historical_values,
                "previsoes": forecasts,
            }

    @staticmethod
    def _forecast_traffic(
        bundle: dict[str, Any], days: int
    ) -> tuple[pd.DatetimeIndex, np.ndarray, np.ndarray, np.ndarray]:
        last_training_date = pd.Timestamp(bundle["ultima_data_treino"])
        index = pd.date_range(last_training_date + pd.Timedelta(days=1), periods=days, freq="D")
        reference_date = pd.Timestamp(bundle["data_referencia"])
        elapsed_days = (index - reference_date).days.to_numpy()
        point_reference = float(bundle["pontos_referencia"])
        future_points = float(bundle["pontos_futuros_assumidos"])
        exog = pd.DataFrame(
            {
                "PONTOS_MEDICAO_REL": future_points / point_reference - 1.0,
                "ANO_SEN": np.sin(2 * np.pi * elapsed_days / 365.25),
                "ANO_COS": np.cos(2 * np.pi * elapsed_days / 365.25),
            },
            index=index,
        )

        result = bundle["modelo"].get_forecast(steps=days, exog=exog)
        confidence = result.conf_int(alpha=0.05)
        return (
            index,
            _restore_scale(result.predicted_mean.to_numpy()),
            _restore_scale(confidence.iloc[:, 0].to_numpy()),
            _restore_scale(confidence.iloc[:, 1].to_numpy()),
        )

    @staticmethod
    def _forecast_accidents(
        bundle: dict[str, Any], index: pd.DatetimeIndex, traffic_volume: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        reference_date = pd.Timestamp(bundle["data_referencia"])
        elapsed_days = (index - reference_date).days.to_numpy()
        week_day = index.dayofweek.to_numpy()
        volume_log_mean = float(bundle["media_volume_log"])
        volume_log_std = float(bundle["desvio_volume_log"])
        exog = pd.DataFrame(
            {
                "VOLUME_LOG_Z": (
                    np.log1p(traffic_volume) - volume_log_mean
                )
                / volume_log_std,
                "SEMANA_SEN": np.sin(2 * np.pi * week_day / 7),
                "SEMANA_COS": np.cos(2 * np.pi * week_day / 7),
                "ANO_SEN": np.sin(2 * np.pi * elapsed_days / 365.25),
                "ANO_COS": np.cos(2 * np.pi * elapsed_days / 365.25),
            },
            index=index,
        )

        result = bundle["modelo"].get_forecast(steps=len(index), exog=exog)
        confidence = result.conf_int(alpha=0.05)
        return (
            _restore_scale(result.predicted_mean.to_numpy()),
            _restore_scale(confidence.iloc[:, 0].to_numpy()),
            _restore_scale(confidence.iloc[:, 1].to_numpy()),
        )


forecast_service = JoblibForecastService()


def assignPredictionModel(api: FastAPI, service: JoblibForecastService = forecast_service) -> None:
    @api.get("/ai/models/status", tags=["IA"])
    async def ai_model_status() -> dict[str, Any]:
        return service.status()

    @api.post("/ai/models/reload", tags=["IA"])
    async def reload_ai_models() -> dict[str, Any]:
        try:
            service.load()
            return service.status()
        except ForecastModelError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    @api.get("/ai/forecast", tags=["IA"])
    @api.get("/predictionData", tags=["IA"], include_in_schema=False)
    async def get_ai_forecast(
        days: int = Query(default=30, ge=1, le=30),
        history_days: int = Query(default=30, ge=1, le=365),
    ) -> dict[str, Any]:
        try:
            return service.forecast(days=days, history_days=history_days)
        except ForecastModelError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
