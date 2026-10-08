from pathlib import Path

import io
import json
import os
import zipfile

from xhtml2pdf import pisa
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from API.model.datasetRequest import DatasetRequest

BASE_DIR_CONTENT = Path(Path(__file__).parent.parent, "content")
BASE_DIR_DATASETS = Path(Path(__file__).parent.parent.parent, "data")

def assignRoutes(api: FastAPI):
    @api.post("/getDataset")
    async def sendDataset(request: DatasetRequest) -> StreamingResponse:
        filepath = Path(BASE_DIR_DATASETS, request.dataset_name, "processed")

        try:
            if not os.path.exists(filepath):
                raise OSError()
            
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for raiz, diretorio, arquivos in os.walk(filepath):
                    for arquivo in arquivos:
                        caminho_completo = Path(raiz, arquivo)
                        caminho_relativo = Path(diretorio, arquivo)

                        zip_file.write(caminho_completo, caminho_relativo)
            
            zip_buffer.seek(0)
            
            return StreamingResponse(
                zip_buffer,
                media_type="application/x-zip-compressed",
                headers={"Content-Disposition": f"attachment; filename={request.dataset_name}_dataset.zip"}
            )
        except OSError:
            raise HTTPException(status_code=503, detail=f"O diretório {filepath} não foi encontrado.")

    @api.get("/listDatasets/")
    async def listDatasets() -> JSONResponse:
        try:
            with open(Path(BASE_DIR_CONTENT, "conjuntos", "content.json"), encoding="utf-8") as file:
                return JSONResponse(content=json.load(file))
        except OSError:
            raise HTTPException(status_code=503, detail=f"O arquivo não foi encontrado.")

    @api.get("/carddata/")
    async def cardData() -> JSONResponse:
        try:
            with open(Path(BASE_DIR_CONTENT, "cards", "content.json"), encoding="utf-8") as file:
                return JSONResponse(content=json.load(file))
        except OSError:
            raise HTTPException(status_code=503, detail=f"O arquivo não foi encontrado.")
        
    @api.get("/statsdata/")
    async def statsData() -> JSONResponse:
        try:
            with open(Path(BASE_DIR_CONTENT, "stats", "content.json"), encoding="utf-8") as file:
                return JSONResponse(content=json.load(file))
        except OSError:
            raise HTTPException(status_code=503, detail=f"O arquivo não foi encontrado.")
    
    @api.get("/accidentHistory")
    async def getAccidentHistory() -> JSONResponse:
        try:
            with open(Path(BASE_DIR_CONTENT, "accident-history", "content.json"), encoding="utf-8") as file:
                return JSONResponse(json.load(file))
        except:
            raise HTTPException(status_code=503, detail=f"O arquivo não foi encontrado.")

    @api.get("/riskData")
    async def getRiskData() -> JSONResponse:
        try:
            with open(Path(BASE_DIR_CONTENT, "accident-history", "risk", "savedData.json"), encoding="utf-8") as file:
                return JSONResponse(json.load(file))
        except OSError:
            raise HTTPException(status_code=503, detail=f"O arquivo não foi encontrado.")

    @api.get("/trafficVolume")
    async def getTrafficVolume() -> JSONResponse:
        try:
            with open(Path(BASE_DIR_CONTENT, "accident-history", "risk", "savedData.json"), encoding="utf-8") as file:
                return JSONResponse(json.load(file))
        except OSError:
            raise HTTPException(status_code=503, detail=f"O arquivo não foi encontrado.")

    @api.get("/generateReport")
    async def generateReport() -> StreamingResponse:
        try:
            with open(Path("..", "reports", "main.html"), "r") as html:
                content = html.read()

            # TODO: Repor valores usando regex ou algo assim

            with io.BytesIO() as pdf:
                pisa.CreatePDF(content, pdf)

            return StreamingResponse(
                pdf,
                media_type="application/pdf",
                headers={"Content-Disposition": "inline; filename=generated.pdf"}
            )
        except OSError:
            raise HTTPException(status_code=503, detail="O relatório não conseguiu ser gerado.")