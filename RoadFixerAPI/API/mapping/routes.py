from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from pathlib import Path
import csv
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "API" / "content/"
ROADFIXER_API_DIR = Path(__file__).resolve().parents[2]
PREDICTION_FILE = ROADFIXER_API_DIR / "ModeloEstatistico" / "data_tau" / "previsao_proximo_mes.csv"

def assignRoutesAPI(api: FastAPI):
    @api.get("/")
    async def root() -> PlainTextResponse:
        return PlainTextResponse("Server Running")
    
    @api.get("/carddata/")
    async def cardData():
        filepath = BASE_DIR / "cards" / "content.json"
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
        
    @api.get("/statsdata/")
    async def statsData():
        filepath = BASE_DIR / "stats" / "content.json"
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    
    @api.get("/accidentHistory")
    async def getAccidentHistory():
        filepath = BASE_DIR / "accident-history" / "content.json"
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)

    @api.get("/riskData")
    async def getRiskData():
        filepath = BASE_DIR / "accident-history" / "risk" / "savedData.json"
        fallback = {
            "last_update": None,
            "risk": [],
            "status": "risk_data_not_generated",
        }

        if not filepath.exists():
            return JSONResponse(content=fallback)

        try:
            with open(filepath, encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            # O arquivo pode estar sendo regravado pelo processamento neste momento.
            return JSONResponse(content=fallback)

    @api.get("/predictionData")
    async def getPredictionData():
        fallback = {
            "period": None,
            "predictions": [],
            "status": "prediction_not_generated",
        }
        if not PREDICTION_FILE.exists():
            return JSONResponse(content=fallback)

        try:
            with open(PREDICTION_FILE, encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            predictions = [
                {"KM": int(float(row["KM"])), "risco": float(row["risco_previsto"])}
                for row in rows
            ]
            predictions.sort(key=lambda prediction: prediction["KM"])
            return {
                "period": rows[0]["PERIODO"] if rows else None,
                "predictions": predictions,
                "status": "ready",
            }
        except (OSError, ValueError, KeyError, csv.Error):
            return JSONResponse(content=fallback)
