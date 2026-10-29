import csv
from datetime import date, timedelta
from pathlib import Path

import io
import json
import os
import zipfile

from xhtml2pdf import pisa
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from functools import lru_cache

from RoadFixerAPI.database import get_database

from ..model.datasetRequest import DatasetRequest

BASE_DIR_CONTENT = Path(Path(__file__).parent.parent, "content")
BASE_DIR_DATASETS = Path(Path(__file__).parent.parent.parent, "data")

def assignRoutes(api: FastAPI):
    @api.post("/getDataset")
    async def sendDataset(request: DatasetRequest) -> StreamingResponse:
        if(request.dataset_name != "weather-data"):
            filepath = Path(BASE_DIR_DATASETS, request.dataset_name, "processed")
        else:
            filepath = Path(BASE_DIR_DATASETS, request.dataset_name)

        try:
            if not os.path.exists(filepath):
                raise OSError()
            
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for raiz, _, arquivos in os.walk(filepath):
                    for arquivo in arquivos:
                        caminho_completo = Path(raiz, arquivo)
                        caminho_relativo = caminho_completo.relative_to(filepath)
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
                content = json.load(file)
        except OSError:
            raise HTTPException(status_code=503, detail="O arquivo não foi encontrado.")

        total = totalAcidentes(Path(BASE_DIR_DATASETS, "accidents", "processed"))
        total_fmt = f"{total:,}".replace(",", ".")  # 12.345 (padrão pt-BR)

        for item in content["content"]:
            item["title"] = item["title"].replace("{total_acidentes}", total_fmt)

        return JSONResponse(content=content)
    
    @api.get("/accidentHistory")
    async def getAccidentHistory() -> JSONResponse:
        hoje = date.today()
        anterior = hoje.replace(day=1) - timedelta(days=1)
        alvo = {(hoje.year, hoje.month), (anterior.year, anterior.month)}

        # em janeiro, o mês anterior é dezembro do ano passado -> lê dois arquivos
        anos = sorted({ano for ano, _ in alvo})

        acidentes = []
        for ano in anos:
            for i, linha in lerAcidentes(ano):
                try:
                    ano_l, mes_l = int(linha["DATA"][:4]), int(linha["DATA"][5:7])
                except (ValueError, KeyError):
                    continue
                if (ano_l, mes_l) in alvo:
                    acidentes.append((linha["DATA"], linha["HORA"], ano, i, linha))

        acidentes.sort(reverse=True)  # mais recentes primeiro

        content = []
        for data, hora, ano, i, linha in acidentes:
            d = date.fromisoformat(data)
            try:
                km = f"{float(linha['KM']):.2f}".replace(".", ",")
            except ValueError:
                km = linha["KM"]

            sentido = linha.get("SENTIDO", "").strip().title()  # NORTE -> Norte

            trecho = f"{linha['RODOVIA']} KM {km}"
            if sentido and sentido.upper() not in {"NÃO INFORMADO", "N/A"}:
                trecho += f" · {sentido}"
            
            content.append({
                "id": f"{ano}-{i}",
                "data": [
                    f"{d.strftime('%d/%m/%Y')} {hora[:5]}",
                    trecho,
                    {"url": f"$server/accidentDetail/{ano}/{i}"},
                ],
            })

        return JSONResponse({"content": content})

    @api.get("/accidentDetail/{ano}/{linha}")
    async def getAccidentDetail(ano: int, linha: int) -> JSONResponse:
        for i, row in lerAcidentes(ano):
            if i == linha:
                return JSONResponse(row)
        raise HTTPException(status_code=404, detail="Acidente não encontrado.")

    @api.get("/riskData")
    async def getRiskData() -> JSONResponse:
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

    @api.get("/predictionData")
    def getPredictionData():
        return get_database().get_predictions()

    def _assinatura(pasta: Path) -> tuple:
        return tuple((p.name, p.stat().st_mtime) for p in sorted(pasta.glob("*.csv")))

    @lru_cache(maxsize=1)
    def _contar_cacheado(pasta_str: str, assinatura: tuple) -> int:
        return contarAcidentes(Path(pasta_str))

    def totalAcidentes(pasta: Path) -> int:
        return _contar_cacheado(str(pasta), _assinatura(pasta))

    def contarAcidentes(pasta: Path) -> int:
        total = 0
        for csv_path in pasta.glob("*.csv"):
            with open(csv_path, encoding="utf-8") as f:
                total += max(sum(1 for _ in f) - 1, 0)  # -1 = cabeçalho
        return total

    def lerAcidentes(ano: int):
        caminho = BASE_DIR_DATASETS / "accidents" / "processed" / f"p{ano}.csv"
        if not caminho.exists():
            return
        with open(caminho, encoding="utf-8", newline="") as f:
            for i, linha in enumerate(csv.DictReader(f)):
                yield i, linha