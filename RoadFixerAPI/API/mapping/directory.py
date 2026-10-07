import io
import json
import os
from pathlib import Path
import zipfile
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
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

    @api.get("/accidentsDatasets")
    async def sendDataset() -> FileResponse:
        pasta_origem = os.path.normpath(os.path.join(".", "data", "accidents", "processed"))
        
        if not os.path.exists(pasta_origem):
            return {"error": f"O diretório {pasta_origem} não foi encontrado."}

        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for raiz, diretorios, arquivos in os.walk(pasta_origem):
                for arquivo in arquivos:
                    caminho_completo = os.path.join(raiz, arquivo)
                    caminho_relativo = os.path.relpath(caminho_completo, pasta_origem)
                    zip_file.write(caminho_completo, caminho_relativo)
                    
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer, 
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": "attachment; filename=accidents_datasets.zip"}
        )
    