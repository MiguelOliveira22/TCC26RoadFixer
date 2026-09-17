from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
from datetime import datetime, date as dt
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "API" / "content/"

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
        filepath = BASE_DIR / "accident-history" / "risk" / "testeSalvo.json"
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
