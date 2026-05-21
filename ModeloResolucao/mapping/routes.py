from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse

from os import path

filepath = "../ConjuntosDados/"

async def assignRoutes(api: FastAPI):
    @api.get("/")
    async def root() -> PlainTextResponse:
        return PlainTextResponse("Server Running")
    
    @api.get("/listadatasets/")
    async def listDatasets():
        return
    
    @api.get("/datasets/")
    async def sendDataset(fileName: str) -> FileResponse:
        return FileResponse(
            path=path.join(filepath, ),
            filename=fileName,
            media_type="application/octet_stream"
        )
    
    @api.get("/a/")
    async def listCards():
        return
    
    @api.get("/as/")
    async def cardData():
        return 
    