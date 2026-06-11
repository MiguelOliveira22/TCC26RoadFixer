import json

from fastapi import FastAPI
from fastapi.responses import FileResponse
from os import path

filepath = "./content/"

def assignRoutesDirectory(api: FastAPI):    
    @api.get("/listadatasets/")
    async def listDatasets():
        with open(path.join(filepath, "conjuntos", "content.json")) as file:
            return json.load(file)
    
    @api.get("/datasets/")
    async def sendDataset() -> FileResponse:
        return FileResponse(
            path=path.join(filepath, "conjuntos"),
            filename="content.json",
            media_type="application/octet_stream"
        )
    