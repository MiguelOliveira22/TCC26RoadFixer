from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
from datetime import datetime

import requests
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

        with open(
            filepath + "accident-history/risk/savedData.json",
            "r+",
            encoding="utf-8",
        ) as savedFile:
            savedData = json.load(savedFile)
            Alteration = False  # Controle para só salvar se houver novos dados

            for file_path in directory.iterdir():
                print(f"Lendo arquivo: {file_path.name}")

                # Pulando arquivos ocultos ou diretórios acidentais (.DS_Store, etc)
                if not file_path.is_file():
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Evita erro caso o arquivo lido esteja sem registros
                    if not data.get("records"):
                        continue

                    # Ignora arquivos antigos baseado no last_update salvo
                    if datetime.fromisoformat(
                        data["records"][0][1]
                    ) < datetime.fromisoformat(savedData["last_update"]):
                        continue

                    Alteration = True

                    records_para_processar = []
                    fields = data["fields"]
                    field_map = {field["id"]: index for index, field in enumerate(fields)}

                    # 1. Agrupa os registros com a HORA exata incluída no dicionário
                    for i in range(0, len(data["records"])):
                        rec = data["records"][i]
                        
                        # Extrai apenas o número da hora (ex: "06:30:00" -> 6)
                        raw_hora = str(rec[field_map.get("HORA")])
                        hora_int = int(raw_hora.split(":")[0]) if ":" in raw_hora else int(raw_hora)

                        records_para_processar.append(
                            {
                                "date": rec[field_map.get("DATA")].split("T")[0].split(" ")[0],
                                "hora": hora_int,
                                "lat": rec[field_map.get("LATITUDE")],
                                "lon": rec[field_map.get("LONGITUDE")],
                                "km": round(float(str(rec[field_map.get("KM")]).replace(",", "."))),
                            }
                        )

                    # 2. Requisições em Lote (Batching)
                    BATCH_SIZE = 100
                    for b in range(0, len(records_para_processar), BATCH_SIZE):
                        batch = records_para_processar[b : b + BATCH_SIZE]

                        lats = [item["lat"] for item in batch]
                        lons = [item["lon"] for item in batch]
                        dates = [item["date"] for item in batch]

                        url = "https://archive-api.open-meteo.com/v1/archive"
                        params = {
                            "latitude": lats,
                            "longitude": lons,
                            "start_date": min(dates),
                            "end_date": max(dates),
                            "hourly": [
                                "temperature_2m",
                                "precipitation",
                                "rain",
                                "weather_code",
                                "wind_speed_10m",
                                "wind_gusts_10m",
                            ],
                            "timezone": "America/Sao_Paulo",
                        }

                        response = requests.get(url, params=params)

                        if response.status_code == 200:
                            res_json = response.json()
                            # Garante que res_json seja uma lista mesmo se o lote tiver 1 elemento só
                            meteo_list = res_json if isinstance(res_json, list) else [res_json]

                            # CORREÇÃO AQUI: Itera item a item emparelhando o registro com a resposta meteorológica
                            for item, meteo_ponto in zip(batch, meteo_list):
                                hourly = meteo_ponto["hourly"]
                                h_idx = item["hora"]  # Pega a hora exata deste acidente específico

                                dados_no_momento_do_acidente = {
                                    "hora": hourly["time"][h_idx],
                                    "chuva": hourly["precipitation"][h_idx],
                                    "vento": hourly["wind_speed_10m"][h_idx],
                                    "rajada": hourly["wind_gusts_10m"][h_idx],
                                    "codigo_tempo": hourly["weather_code"][h_idx],
                                }

                                print(dados_no_momento_do_acidente)

                        # Atualização dos riscos
                        for item in batch:
                            savedData["risk"][item["km"]] += 1
                            savedData["last_update"] = item["date"]

            # SALVAMENTO AUTOMÁTICO
            if Alteration:
                print("att")
                savedFile.seek(0)
                savedFile.truncate()
                json.dump(savedData, savedFile, indent=4)

        return {"status": "Processamento concluído com sucesso"}

    # exemplo de retorno do site open-meteo
    '''
    [
        {
            "latitude": -22.90,
            "longitude": -47.05,
            "timezone": "America/Sao_Paulo",
            "hourly_units": {
            "time": "iso8601",
            "precipitation": "mm",
            "wind_speed_10m": "km/h"
            },
            "hourly": {
            "time": ["2024-01-08T00:00", "2024-01-08T01:00", "..."],
            "precipitation": [0.0, 0.0, 12.5, "..."],
            "rain": [0.0, 0.0, 12.5, "..."],
            "temperature_2m": [22.1, 21.8, 20.4, "..."],
            "weather_code": [0, 0, 61, "..."],
            "wind_speed_10m": [10.2, 11.5, 25.0, "..."],
            "wind_gusts_10m": [15.0, 18.2, 45.1, "..."]
            }
        },
        {
            "latitude": -22.95,
            "longitude": -47.09,
            "...": "Mesma estrutura para o Ponto B"
        },
        {
            "latitude": -22.99,
            "longitude": -47.12,
            "...": "Mesma estrutura para o Ponto C"
        }
    ]
    '''