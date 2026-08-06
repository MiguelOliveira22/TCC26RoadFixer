from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
from datetime import datetime

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
    
    @api.get("/accidentHistory")
    async def getAccidentHistory():
        with open(filepath + "accident-history/content.json") as file:
            return json.load(file)

    @api.get("/calcAccidents")
    async def calcAccidents():
        directory = Path(filepath + "accident-history/data")
        
        with open(filepath + "accident-history/risk/savedData.json", "r+", encoding="utf-8") as savedFile:
            savedData = json.load(savedFile)
            houve_alteracao = False # Controle para só salvar se houver novos dados

            for file_path in directory.iterdir():
                print(file_path.name)
                # Pulando arquivos ocultos ou diretórios acidentais (.DS_Store, etc)
                if not file_path.is_file():
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Evita erro caso o arquivo lido esteja sem registros
                    if not data.get("records"):
                        continue

                    # Ignora arquivos antigos baseado no last_update salvo
                    if datetime.fromisoformat(data["records"][0][1]) < datetime.fromisoformat(savedData["last_update"]):
                        continue

                    houve_alteracao = True

                    # Processa os registros de trás para frente
                    for i in range(len(data["records"]) - 1, 0, -1):

                        ''' Alterar a função que calcula o risco aqui'''

                        indice_risk = round(float(data["records"][i][7].replace(",", ".")))
                        
                        if 0 <= indice_risk < len(savedData["risk"]):
                            savedData["risk"][indice_risk] += 1

                        savedData["last_update"] = data["records"][i][1]
                        ''' Fim da função'''

            # SALVAMENTO AUTOMÁTICO: Fora de todos os loops
            if houve_alteracao:
                print("att")
                savedFile.seek(0)
                savedFile.truncate()
                json.dump(savedData, savedFile, indent=4) # json.dump (sem "s") grava no arquivo

        return {"status": "Processamento concluído com sucesso"}