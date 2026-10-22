import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pandas as pd

from RoadFixerAPI.database import Database
from RoadFixerAPI.API.mapping.routes import assignRoutesAPI
from RoadFixerAPI.API.mapping.directory import assignRoutesDirectory
from RoadFixerAPI.ModeloEstatistico.core import riskCalculations
from RoadFixerAPI.ModeloEstatistico import grid_search
from RoadFixerAPI.ProcessamentoParametros import updateData


def accident(**overrides):
    return {
        "DATA": "2025-01-01", "HORA": "09:14:00", "KM": 1.0,
        "RODOVIA": "SP330", "LATITUDE": -21.2, "LONGITUDE": -47.7,
        "CLASSE": "CHOQUE", "SUBCLASSE": "CHOQUE-OBJETO NA PISTA",
        "VITIMA_LEVE": 1, "VITIMA_MODERADA": 0, "VITIMA_GRAVE": 0,
        "VITIMA_FATAL": 0, "NUMVEÍCULOS": 1, **overrides,
    }


class DuckDBTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.seeds = self.root / "seeds"
        self.db = Database(self.root / "roadfixer.duckdb", self.seeds)

    def client(self):
        app = FastAPI()
        assignRoutesAPI(app)
        assignRoutesDirectory(app)
        for module in ("routes", "directory"):
            patcher = patch(f"RoadFixerAPI.API.mapping.{module}.get_database", return_value=self.db)
            patcher.start()
            self.addCleanup(patcher.stop)
        client = TestClient(app)
        self.addCleanup(client.close)
        return client

    def write_json(self, path, value):
        path = self.seeds / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_csv(self, path, frame):
        path = self.seeds / path
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)

    def test_migration_preserves_http_contract_and_survives_missing_sources(self):
        documents = {"cards": {"cards": [1]}, "stats": [2],
                     "accident-history": {"history": [3]}, "conjuntos": {"content": [4]}}
        for folder, value in documents.items():
            self.write_json(f"API/content/{folder}/content.json", value)
        risk = {"last_update": "2026-10-01", "risk": [0, 2.5, 8]}
        self.write_json("API/content/accident-history/risk/savedData.json", risk)
        self.write_csv("data/accidents/processed/p2025.csv", pd.DataFrame([accident()]))
        self.write_csv("data/weather-data/p2025.csv", pd.DataFrame([{
            "DATAHORA": "2025-01-01 09:14:00", "CHUVA": 0,
        }]))
        self.write_csv("ModeloEstatistico/data_tau/tau.csv", pd.DataFrame([{
            "CLASSE": "CHOQUE", "SUBCLASSE": "CHOQUE-OBJETO NA PISTA", "TAU": 1,
        }]))
        self.write_csv("ModeloEstatistico/data_tau/previsao_proximo_mes.csv", pd.DataFrame([
            {"PERIODO": "2026-11", "KM": 2, "risco_previsto": 4.5},
            {"PERIODO": "2026-11", "KM": 1, "risco_previsto": 3.0},
        ]))
        self.db.initialize()
        self.assertEqual(len(self.db.load_accidents()), 1)
        self.assertEqual(len(self.db.load_weather("p2025.csv")), 1)
        self.assertEqual(len(self.db.load_tau()), 1)
        # Uma nova instância não deve depender dos CSVs/JSONs já importados.
        self.seeds.rename(self.root / "archived")
        self.db = Database(self.db.path, self.seeds)
        client = self.client()
        for route, folder in (("/carddata/", "cards"), ("/statsdata/", "stats"),
                              ("/accidentHistory", "accident-history"), ("/listadatasets/", "conjuntos")):
            self.assertEqual(client.get(route).json(), documents[folder])
        self.assertEqual(client.get("/riskData").json(), risk)
        self.assertEqual(client.get("/predictionData").json(), {
            "period": "2026-11", "status": "ready",
            "predictions": [{"KM": 1, "risco": 3.0}, {"KM": 2, "risco": 4.5}],
        })
        download = client.get("/datasets/")
        self.assertEqual(json.loads(download.content), documents["conjuntos"])
        self.assertIn('filename="content.json"', download.headers["content-disposition"])
        self.db.save_risk({"last_update": "new", "risk": [7]})
        self.assertEqual(Database(self.db.path, self.root / "archived").get_risk()["risk"], [7])

    def test_empty_database_has_safe_fallbacks(self):
        client = self.client()
        self.assertEqual(client.get("/").text, "Server Running")
        self.assertEqual(client.get("/riskData").json(), {
            "last_update": None, "risk": [], "status": "risk_data_not_generated",
        })
        self.assertEqual(client.get("/predictionData").json(), {
            "period": None, "predictions": [], "status": "prediction_not_generated",
        })

    def test_replacing_year_preserves_other_years_and_accepts_new_columns(self):
        self.db.save_accidents("p2024.csv", pd.DataFrame([accident(KM=4)]))
        self.db.save_accidents("p2025.csv", pd.DataFrame([accident(KM=5), accident(KM=6)]))
        self.db.save_accidents("p2025.csv", pd.DataFrame([accident(KM=7, NEW_FIELD="value")]))
        self.assertEqual(sorted(self.db.load_accidents()["KM"].tolist()), [4, 7])
        self.assertEqual(self.db.load_accidents("p2025.csv")["NEW_FIELD"].iloc[0], "value")
        self.assertEqual(self.db.accident_sources(), ["p2024.csv", "p2025.csv"])

    def test_failed_publication_rolls_back_and_concurrent_reads_are_consistent(self):
        original = {"last_update": "1", "risk": [1.0]}
        self.db.save_risk(original)
        with patch.object(self.db, "_put_document", side_effect=RuntimeError("publication failed")):
            with self.assertRaises(RuntimeError):
                self.db.save_risk({"last_update": "2", "risk": [2.0]})
        self.assertEqual(self.db.get_risk(), original)
        with self.assertRaises(ValueError):
            self.db.save_risk({"risk": [float("nan")]})
        forecast = pd.DataFrame([{"PERIODO": "2026-11", "KM": 1, "risco_previsto": 2.0}])
        self.db.save_predictions(forecast)
        before = self.db.get_predictions()
        forecast["risco_previsto"] = float("inf")
        with self.assertRaises(ValueError):
            self.db.save_predictions(forecast)
        self.assertEqual(self.db.get_predictions(), before)

        def update_and_read(value):
            self.db.save_risk({"last_update": str(value), "risk": [value] * 3})
            result = self.db.get_risk()
            self.assertEqual(result["risk"], [float(result["last_update"])] * 3)

        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(update_and_read, range(8)))

    def test_artesp_update_publishes_corridor_to_database(self):
        response = Mock(content=pd.DataFrame([
            accident(RODOVIA="SP330"), accident(RODOVIA="SPA330"), accident(RODOVIA="SP348"),
        ]).to_csv(index=False).encode())
        raw_dir = self.root / "raw"
        (raw_dir / "non_Processed").mkdir(parents=True)
        with patch.object(updateData, "get_database", return_value=self.db), \
             patch.object(updateData, "prepararPastas", return_value=(raw_dir, self.root)), \
             patch.object(updateData.requests, "get", return_value=response):
            self.assertTrue(updateData.atualizarARTESP())
        self.assertEqual(set(self.db.load_accidents()["RODOVIA"]), {"SP330", "SPA330"})
        self.assertFalse((raw_dir / "processed").exists())

    def test_risk_calculation_saves_weather_and_reuses_database_cache(self):
        self.db.save_accidents("p2025.csv", pd.DataFrame([accident()]))
        with self.db.connection() as connection:
            connection.execute("INSERT INTO tau VALUES ('CHOQUE', 'CHOQUE-OBJETO NA PISTA', 1)")
        response = Mock(status_code=200)
        response.json.return_value = {"hourly": {
            "time": ["2025-01-01T09:00"], "precipitation": [1.0],
            "wind_speed_10m": [2.0], "wind_gusts_10m": [3.0], "weather_code": [4],
        }}
        with patch.object(riskCalculations, "get_database", return_value=self.db), \
             patch.object(riskCalculations.requests, "get", return_value=response) as request:
            riskCalculations.calcAccidents()
            first = self.db.get_risk()
            riskCalculations.calcAccidents()
        self.assertEqual(request.call_count, 1)
        self.assertEqual(first, self.db.get_risk())
        self.assertGreater(first["risk"][1], first["risk"][0])
        self.assertEqual(len(self.db.load_weather("p2025.csv")), 1)

    def test_extra_trees_reads_database_and_publishes_prediction(self):
        frame = pd.DataFrame([
            accident(DATA=str(period.start_time.date()), KM=km, VITIMA_LEVE=km)
            for period in pd.period_range("2023-01", "2025-12", freq="M")
            for km in (1, 2)
        ])
        self.db.save_accidents("p2025.csv", frame)
        # A ARTESP entrega DATA como datetime; o legado contém strings de data.
        self.db.save_accidents("p2026.csv", pd.DataFrame([
            accident(DATA=pd.Timestamp("2026-01-01")),
        ]))
        output = self.root / "model" / "report.json"
        with patch.object(grid_search, "get_database", return_value=self.db), \
             patch.object(grid_search, "DEFAULT_OUTPUT", output):
            self.assertEqual(len(grid_search.load_accidents(grid_search.DEFAULT_DATA_DIR)), 73)
            report = grid_search.run(output=output, external_dir=None)
        forecast = self.db.get_predictions()
        self.assertEqual(report["proximo_periodo_previsto"], "2026-02")
        self.assertEqual(forecast["period"], "2026-02")
        self.assertEqual([row["KM"] for row in forecast["predictions"]], [1, 2])
        self.assertTrue(all(row["risco"] >= 0 for row in forecast["predictions"]))
        self.assertTrue(output.with_name("previsao_proximo_mes.csv").exists())


if __name__ == "__main__":
    unittest.main()
