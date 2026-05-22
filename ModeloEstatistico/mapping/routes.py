from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse

from os import path

filepath = "../ConjuntosDados/"

def assignRoutes(api: FastAPI):
    @api.get("/")
    async def root() -> PlainTextResponse:
        return PlainTextResponse("Server Running")
    
    @api.get("/graphdata/")
    async def graphdata(start: int, size: int):
        return
    