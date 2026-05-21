from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from os import path

filepath = "../ConjuntosDados/"

async def assignRoutesAPI(api: FastAPI):
    @api.get("/")
    async def root() -> PlainTextResponse:
        return PlainTextResponse("Server Running")
    
    @api.get("/a/")
    async def listCards():
        return 
    
    @api.get("/as/")
    async def cardData():
        return 
    
    @api.get("/asd/")
    async def footerLinks():
        return
    
    @api.get("/asdf/")
    async def footerEmails():
        return
    