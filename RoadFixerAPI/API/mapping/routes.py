from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
from datetime import datetime, date as dt

import json

filepath = "./content/"

def assignRoutesAPI(api: FastAPI):
    @api.get("/")
    async def root() -> PlainTextResponse:
        return PlainTextResponse("Server Running")
    
    @api.get("/carddata/")
    async def cardData():
        with open(filepath + "cards/content.json") as file:
            return json.load(file)
        
    @api.get("/statsdata/")
    async def statsData():
        with open(filepath + "stats/content.json") as file:
            return json.load(file)
    
    @api.get("/accidentHistory")
    async def getAccidentHistory():
        with open(filepath + "accident-history/content.json") as file:
            return json.load(file)

    @api.get("/riskData")
    async def getRiskData():
<<<<<<< Updated upstream
        with open(filepath + "accident-history/risk/testeSalvo.json") as file:
=======
        # ``savedData`` é a saída publicada pelo treinamento. ``testeSalvo``
        # é apenas uma fixture zerada e não representa a previsão da IA.
        filepath = BASE_DIR / "accident-history" / "risk" / "savedData.json"
        with open(filepath, encoding="utf-8") as file:
>>>>>>> Stashed changes
            return json.load(file)
