from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
from datetime import datetime

import requests
import json
import random
import pandas as pd

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

                # Pulando arquivos ocultos, diretórios acidentais (.DS_Store, etc)
                # e qualquer coisa que não seja .csv
                if not file_path.is_file() or file_path.suffix.lower() != ".csv":
                    continue

                # pandas já lê o CSV inteiro e monta uma tabela (DataFrame),
                # usando a primeira linha do arquivo como nome das colunas
                df = pd.read_csv(file_path, encoding="utf-8")

                # Evita erro caso o arquivo lido esteja sem registros
                if df.empty:
                    continue

                # Ignora arquivos antigos baseado no last_update salvo
                # (equivalente ao antigo data["records"][0][1], agora é a
                # primeira linha da coluna DATA)
                primeira_data = str(df["DATA"].iloc[0])
                if datetime.fromisoformat(primeira_data) < datetime.fromisoformat(
                    savedData["last_update"]
                ):
                    continue

                Alteration = True

                # 1. Monta as colunas derivadas direto no DataFrame (bem mais
                # rápido do que fazer um for linha a linha em Python puro)

                # Extrai apenas a data, sem hora (ex: "2026-01-01T00:00:00" -> "2026-01-01")
                df["date"] = df["DATA"].astype(str).str.split("T").str[0].str.split(" ").str[0]

                # Extrai apenas o número da hora (ex: "06:30:00" -> 6)
                df["hora"] = df["HORA"].astype(str).str.split(":").str[0].astype(int)

                # KM: troca vírgula por ponto (padrão BR -> padrão numérico) e arredonda
                df["km"] = (
                    df["KM"].astype(str).str.replace(",", ".", regex=False).astype(float).round().astype(int)
                )

                # Descarta linhas sem LATITUDE/LONGITUDE (não dá pra consultar
                # clima sem coordenada, e mandar NaN pro open-meteo quebra o request)
                antes = len(df)
                df = df.dropna(subset=["LATITUDE", "LONGITUDE"])
                if len(df) < antes:
                    print(f"Aviso: {antes - len(df)} linha(s) descartada(s) por falta de LATITUDE/LONGITUDE")

                # Ordena por data: o arquivo não vem necessariamente em ordem
                # cronológica, e sem isso um mesmo lote de 100 pode misturar
                # datas de meses bem diferentes, deixando o intervalo
                # start_date/end_date do open-meteo gigante (e o request lento/travando)
                df = df.sort_values("date").reset_index(drop=True)

                # Converte o DataFrame em uma lista de dicionários, no mesmo
                # formato que o resto do código já espera: {"date", "hora", "lat", "lon", "km"}
                records_para_processar = df[["date", "hora", "LATITUDE", "LONGITUDE", "km"]].rename(
                    columns={"LATITUDE": "lat", "LONGITUDE": "lon"}
                ).to_dict("records")

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

                    # timeout=30 evita que o request fique preso pra sempre
                    # se o open-meteo não responder (era isso que estava
                    # "travando" o servidor até o proxy devolver 500)
                    try:
                        response = requests.get(url, params=params, timeout=30)
                    except requests.exceptions.RequestException as e:
                        print(f"Erro ao chamar open-meteo no lote {b}: {e}")
                        continue

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

                    else:
                        print(f"open-meteo devolveu {response.status_code} no lote {b}: {response.text[:200]}")

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