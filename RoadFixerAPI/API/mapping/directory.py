import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from os import path

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "API" / "content/"

def assignRoutesDirectory(api: FastAPI):    
    @api.get("/listadatasets/")
    async def listDatasets():
        with open(path.join(BASE_DIR, "conjuntos", "content.json")) as file:
            return json.load(file)
    
    @api.get("/datasets/")
    async def sendDataset() -> FileResponse:
        return FileResponse(
            path=path.join(BASE_DIR, "conjuntos", "content.json"),
            filename="content.json",
            media_type="application/octet_stream"
        )
    