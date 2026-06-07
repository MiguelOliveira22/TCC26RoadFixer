from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse

import json
import random

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
    
    @api.get("/asd/")
    async def footerLinks():
        return
    
    @api.get("/asdf/")
    async def footerEmails():
        return
    
    @api.get("/riskData/")
    async def getRiskData():
        risk = [random.random()*10 for _ in range(453)]
        return risk
        