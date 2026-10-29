import os
import unittest

from fastapi.testclient import TestClient

os.environ["ROADFIXER_AUTO_UPDATE"] = "0"

from RoadFixerAPI.API.main import server  # noqa: E402
from RoadFixerAPI.API.mapping.predictions import forecast_service  # noqa: E402


class JoblibForecastServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        forecast_service.load()

    def test_forecast_encadeia_sarimax_e_arimax(self):
        result = forecast_service.forecast(days=7, history_days=30)

        self.assertEqual(result["periodo"]["dias"], 7)
        self.assertEqual(len(result["previsoes"]), 7)
        self.assertEqual(result["periodo_historico"]["dias"], 30)
        self.assertEqual(len(result["historico"]), 30)
        self.assertEqual(result["modelos"]["trafego"]["tipo"], "SARIMAX")
        self.assertEqual(result["modelos"]["acidentes"]["tipo"], "ARIMAX")

        last_observed = result["historico"][-1]
        first_forecast = result["previsoes"][0]
        self.assertEqual(last_observed["data"], "2026-08-09")
        self.assertEqual(first_forecast["data"], "2026-08-10")
        self.assertGreater(last_observed["volume_trafego"]["observado"], 0)
        self.assertGreaterEqual(last_observed["acidentes"]["observado"], 0)

        for forecast in result["previsoes"]:
            traffic = forecast["volume_trafego"]
            accidents = forecast["acidentes"]
            self.assertGreater(traffic["previsao"], 0)
            self.assertLessEqual(traffic["limite_inferior_95"], traffic["previsao"])
            self.assertGreaterEqual(traffic["limite_superior_95"], traffic["previsao"])
            self.assertGreaterEqual(accidents["previsao"], 0)
            self.assertLessEqual(accidents["limite_inferior_95"], accidents["previsao"])
            self.assertGreaterEqual(accidents["limite_superior_95"], accidents["previsao"])

    def test_endpoint_publica_previsao_e_status(self):
        with TestClient(server) as client:
            status = client.get("/ai/models/status")
            forecast = client.get(
                "/ai/forecast", params={"days": 3, "history_days": 7}
            )

        self.assertEqual(status.status_code, 200)
        self.assertTrue(status.json()["carregado"])
        self.assertEqual(forecast.status_code, 200)
        self.assertEqual(len(forecast.json()["previsoes"]), 3)
        self.assertEqual(len(forecast.json()["historico"]), 7)

    def test_endpoint_rejeita_horizonte_maior_que_trinta_dias(self):
        with TestClient(server) as client:
            response = client.get("/ai/forecast", params={"days": 31})

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
