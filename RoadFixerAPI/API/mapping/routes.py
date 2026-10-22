from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from RoadFixerAPI.database import get_database


def assignRoutesAPI(api: FastAPI):
    @api.get("/")
    async def root() -> PlainTextResponse:
        return PlainTextResponse("Server Running")

    @api.get("/carddata/")
    def cardData():
        return get_database().get_document("cards")

    @api.get("/statsdata/")
    def statsData():
        return get_database().get_document("stats")

    @api.get("/accidentHistory")
    def getAccidentHistory():
        return get_database().get_document("history")

    @api.get("/riskData")
    def getRiskData():
        return get_database().get_risk()

    @api.get("/predictionData")
    def getPredictionData():
        return get_database().get_predictions()
