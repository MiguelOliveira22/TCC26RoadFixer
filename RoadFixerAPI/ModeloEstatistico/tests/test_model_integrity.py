from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from RoadFixerAPI.ModeloEstatistico.context_features import add_traffic
from RoadFixerAPI.ModeloEstatistico.core.riskCalculations import (
    calculateFatorClimatico,
    calculateGravity,
)
from RoadFixerAPI.ModeloEstatistico.grid_search import emergency_capture, make_dataset


class ModelIntegrityTests(unittest.TestCase):
    def test_gravity_keeps_fatal_weight_in_fatal_argument(self):
        self.assertEqual(calculateGravity(0, 0, 0, 1), 14.0)
        self.assertEqual(calculateGravity(1, 1, 1, 1, 99), 22.0)

    def test_rain_is_neutral_or_increases_historical_risk(self):
        self.assertEqual(calculateFatorClimatico({"CHUVA": 0}), 1.0)
        self.assertGreater(calculateFatorClimatico({"CHUVA": 20}), 1.0)
        self.assertEqual(calculateFatorClimatico({"CHUVA": 20}), 1.5)

    def test_capture_accepts_non_sequential_indexes(self):
        actual = pd.Series([0, 8, 2], index=[12, 18, 44])
        predicted = pd.Series([0.1, 0.9, 0.2], index=[12, 18, 44])
        self.assertEqual(emergency_capture(actual, predicted, 1 / 3), 0.8)

    def test_forecast_month_has_no_observed_target_and_only_uses_past(self):
        accidents = pd.DataFrame(
            {
                "DATA": pd.to_datetime(["2025-01-05", "2025-02-06"]),
                "KM": [10, 10],
                "VITIMA_LEVE": [1, 0],
                "VITIMA_MODERADA": [0, 1],
                "VITIMA_GRAVE": [0, 0],
                "VITIMA_FATAL": [0, 0],
                "SEVERIDADE": [1, 2],
            }
        )
        panel = make_dataset(accidents, external_dir=None, inmet_dir=None, include_forecast_month=True)
        march = panel[(panel["PERIODO"] == pd.Period("2025-03", freq="M")) & (panel["KM"] == 10)].iloc[0]
        self.assertFalse(march["alvo_observado"])
        self.assertTrue(pd.isna(march["severidade"]))
        self.assertEqual(march["severidade_30d"], 2)

    def test_traffic_is_shifted_to_the_next_month(self):
        panel = pd.DataFrame({"PERIODO": pd.period_range("2025-01", "2025-02", freq="M"), "KM": [10, 10]})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "traffic.csv"
            pd.DataFrame({"data": ["2025-01-01"], "km": [10], "volume_total": [100]}).to_csv(path, index=False)
            result = add_traffic(panel, path)
        self.assertTrue(pd.isna(result.loc[0, "fluxo_total"]))
        self.assertEqual(result.loc[1, "fluxo_total"], 100)


if __name__ == "__main__":
    unittest.main()
