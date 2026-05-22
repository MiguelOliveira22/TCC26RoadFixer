from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from os import path

filepath = "../ConjuntosDados/"

def assignRoutesDirectory(api: FastAPI):    
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
    