from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
from datetime import datetime, date as dt

import requests
import json
import random
import pandas as pd
import time
import statistics
import math

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
    
    @api.get("/asdata/")
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
            filepath + "formula/tau.csv",
        ) as tauTableFile:
            TAU_TABLE = pd.read_csv(tauTableFile.name, encoding="utf-8")
            with open(
                filepath + "accident-history/risk/savedData.json",
                "r+",
                encoding="utf-8",
            ) as savedatafile:
                countFilesData = 0
                savedData = json.load(savedatafile)
                newData = [0] * len(savedData["risk"])

                for file_path in directory.iterdir():
                    print(f"Lendo arquivo: {file_path.name}")

                    # Pulando arquivos ocultos, diretórios acidentais (.DS_Store, etc)
                    # e qualquer coisa que não seja .csv
                    if not file_path.is_file() or file_path.suffix.lower() != ".csv":
                        continue

                    # pandas já lê o CSV inteiro e monta uma tabela (DataFrame),
                    # usando a primeira linha do arquivo como nome das colunas
                    data = pd.read_csv(file_path, encoding="utf-8")

                    # Evita erro caso o arquivo lido esteja sem registros
                    if data.empty:
                        continue

                    countFilesData += 1

                    # 1. Monta as colunas derivadas direto no DataFrame (bem mais
                    # rápido do que fazer um for linha a linha em Python puro)

                    # Extrai apenas a data, sem hora (ex: "2026-01-01T00:00:00" -> "2026-01-01")
                    data["date"] = data["DATA"].astype(str).str.split("T").str[0].str.split(" ").str[0]

                    # Extrai apenas o número da hora (ex: "06:30:00" -> 6)
                    data["hora"] = data["HORA"].astype(str).str.split(":").str[0].astype(int)

                    # KM: troca vírgula por ponto (padrão BR -> padrão numérico) e arredonda
                    data["KM"] = (
                        data["KM"].astype(str).str.replace(",", ".", regex=False).astype(float).round().astype(int)
                    )

                    # Descarta linhas sem LATITUDE/LONGITUDE (não dá pra consultar
                    # clima sem coordenada, e mandar NaN pro open-meteo quebra o request)
                    antes = len(data)
                    data = data.dropna(subset=["LATITUDE", "LONGITUDE"])
                    if len(data) < antes:
                        print(f"Aviso: {antes - len(data)} linha(s) descartada(s) por falta de LATITUDE/LONGITUDE")

                    # Converte o DataFrame em uma lista de dicionários, no mesmo
                    # formato que o resto do código já espera: {"date", "hora", "lat", "lon", "KM"}
                    records_para_processar = data[["date", "hora", "LATITUDE", "LONGITUDE", "KM", "CLASSE", "SUBCLASSE", "VITIMA_ILESA" , "VITIMA_LEVE", "VITIMA_MODERADA", "VITIMA_GRAVE", "VITIMA_FATAL"]].rename(
                        columns={"LATITUDE": "lat", "LONGITUDE": "lon", "VITIMA_ILESA": "VI", "VITIMA_LEVE": "VL", "VITIMA_MODERADA": "VM", "VITIMA_GRAVE": "VG", "VITIMA_FATAL": "VF"}
                    ).to_dict("records")

                    # 2. Requisições em Lote (Batching)
                    BATCH_SIZE = 100
                    MAX_RETRIES = 5
                    for b in range(0, len(records_para_processar), BATCH_SIZE):
                        batch = records_para_processar[b : b + BATCH_SIZE]

                        lats = [acidente["lat"] for acidente in batch]
                        lons = [acidente["lon"] for acidente in batch]
                        dates = [acidente["date"] for acidente in batch]

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

                        response = None
                        for tentativa in range(MAX_RETRIES):
                            try:
                                response = requests.get(url, params=params, timeout=30)
                            except requests.exceptions.RequestException as e:
                                print(f"Erro ao chamar open-meteo no lote {b}: {e}")
                                break

                            if response.status_code == 429:
                                espera = int(response.headers.get("Retry-After", 60))
                                print(f"Rate limit no lote {b}, aguardando {espera}s (tentativa {tentativa + 1}/{MAX_RETRIES})")
                                time.sleep(espera)
                                continue  # tenta de novo

                            break  # não foi 429 (deu certo ou foi outro erro), sai do retry

                        if response is None:
                            continue  # falhou de vez (erro de conexão), pula o lote

                        if response.status_code == 200:
                            res_json = response.json()
                            # Garante que res_json seja uma lista mesmo se o lote tiver 1 elemento só
                            meteo_list = res_json if isinstance(res_json, list) else [res_json]

                            # Itera acidente a acidente emparelhando o registro com a resposta meteorológica
                            for acidente, meteo_ponto in zip(batch, meteo_list):
                                hourly = meteo_ponto["hourly"]

                                # timestamp exato do acidente, no mesmo formato que vem em hourly["time"]
                                timestamp_alvo = f"{acidente['date']}T{acidente['hora']:02d}:00"

                                try:
                                    h_idx = hourly["time"].index(timestamp_alvo)
                                except ValueError:
                                    print(f"Timestamp {timestamp_alvo} não encontrado no retorno do open-meteo")
                                    continue

                                dados_no_momento_do_acidente = {
                                    "hora": hourly["time"][h_idx],
                                    "chuva": hourly["precipitation"][h_idx],
                                    "vento": hourly["wind_speed_10m"][h_idx],
                                    "rajada": hourly["wind_gusts_10m"][h_idx],
                                    "codigo_tempo": hourly["weather_code"][h_idx],
                                }

                                newData[acidente["KM"]] += calcGravity(acidente["VI"], acidente["VL"], acidente["VM"], acidente["VG"], acidente["VF"]) * calcFatorClimatico(dados_no_momento_do_acidente) * calcRecencia(acidente) * calcTau(TAU_TABLE, acidente)

                        elif response.status_code == 429:
                            print(f"Lote {b} falhou após {MAX_RETRIES} tentativas por rate limit — pulado")
                            continue
                        else:
                            print(f"open-meteo devolveu {response.status_code} no lote {b}: {response.text[:200]}")


                # Atualização dos riscos

                if(countFilesData > 0):
                    for i in range(len(newData)):
                        newData[i] = newData[i]/countFilesData

                    media = sum(newData) / len(newData)
                    desvio_padrao = statistics.pstdev(newData)

                    for i in range(len(newData)):
                        savedData["risk"][i] = 10 / (1 + math.pow(math.e, -((newData[i] - media) / desvio_padrao)))

                    savedData["last_update"] = dt.today().strftime("%Y-%m-%d")
                        
                    # SALVAMENTO AUTOMÁTICO
                    print("att")
                    savedatafile.seek(0)
                    savedatafile.truncate()
                    json.dump(savedData, savedatafile, indent=4)

        return {"status": "Processamento concluído com sucesso"}

    def calcGravity(vi, vl, vm, vg, vf):
        return (13*vf) + (5*vg) + (2*vm) + vl

    def calcFatorClimatico(clima):
        return 1.3 - (0.5 * min(1, clima["chuva"] / 20))

    def calcRecencia(acidente):
        data_comparar = datetime.strptime(acidente["date"], "%Y-%m-%d")
        hoje = datetime.today()
        diferenca_anos = (hoje.year - data_comparar.year - ((hoje.month, hoje.day) < (data_comparar.month, data_comparar.day)))
        return math.pow(math.e, -((math.log(2) / 3) * diferenca_anos))

    def calcTau(tauTable, acidente):
        resultado = tauTable.loc[
            (tauTable["CLASSE"] == acidente["CLASSE"]) & 
            (tauTable["SUBCLASSE"] == acidente["SUBCLASSE"]), 
            "τ"
        ]

        # 2. Verifica se encontrou algo antes de acessar o índice [0]
        return resultado.values[0] if not resultado.empty else 0

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