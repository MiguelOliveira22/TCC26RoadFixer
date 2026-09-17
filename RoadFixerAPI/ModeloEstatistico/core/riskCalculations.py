from datetime import datetime
import os
from pathlib import Path

import requests
import json
import pandas as pd
import time
import statistics
import math

filepath = Path("./ModeloEstatistico/data_tau")
filepathRisk = Path("./API/content/accident-history")
filepathWeather = Path("./data/weather-data")

TAUTABLE = pd.read_csv(str(filepath) + "/tau.csv", encoding="utf-8")

def calcAccidents():
    directory = Path(filepath)

    with open(
        Path(filepathRisk, "risk/savedData.json"),
        "r+",
        encoding="utf-8",
    ) as savedatafile:
        countFilesData = 0
        savedData = json.load(savedatafile)
        newData = [0] * len(savedData["risk"])

        for file_path in directory.iterdir():
            fileWeather = Path(filepathWeather, file_path.name)
            if os.path.exists(fileWeather):
                weatherAtual = pd.read_csv(fileWeather)
            else:
                weatherAtual = None

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
            records_para_processar = data.rename(columns={"LATITUDE": "lat", "LONGITUDE": "lon", "VITIMA_LEVE": "VL", "VITIMA_MODERADA": "VM", "VITIMA_GRAVE": "VG", "VITIMA_FATAL": "VF"}).to_dict("records")

            # 2. Requisições em Lote (Batching)
            BATCH_SIZE = 100
            MAX_RETRIES = 5
            for b in range(0, len(records_para_processar), BATCH_SIZE):
                batch = records_para_processar[b : b + BATCH_SIZE]

                lats = [acidente["lat"] for acidente in batch]
                lons = [acidente["lon"] for acidente in batch]
                dates = [acidente["DATA"] for acidente in batch]

                todos_presentes = False

                if weatherAtual is not None:
                    datetimes = [pd.to_datetime(f"{acidente['DATA']} {acidente['HORA']}") for acidente in batch]
                    existentes = set(pd.to_datetime(weatherAtual["DATAHORA"]))
                    todos_presentes = all(dt in existentes for dt in datetimes)

                if todos_presentes:
                    for acidente in zip(batch):
                        dados_no_momento_do_acidente = weatherAtual[(weatherAtual["DATA"] == acidente["date"]) & (weatherAtual["HORA"] == acidente["HORA"])].to_json()
                        newData[acidente["KM"]] += calculateGravity(acidente["VL"], acidente["VM"], acidente["VG"], acidente["VF"], acidente["NUMVEÍCULOS"]) * calculateFatorClimatico(dados_no_momento_do_acidente) * calculateRecencia(acidente) * getRiskFromTauTable(acidente)

                else:
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

                    elif response.status_code == 429:
                        print(f"Lote {b} falhou após {MAX_RETRIES} tentativas por rate limit — pulado")
                        continue

                    elif response.status_code != 200:
                        print(f"open-meteo devolveu {response.status_code} no lote {b}: {response.text[:200]}")

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

                        newData[acidente["KM"]] += calculateGravity(acidente["VL"], acidente["VM"], acidente["VG"], acidente["VF"], acidente["NUMVEÍCULOS"]) * calculateFatorClimatico(dados_no_momento_do_acidente) * calculateRecencia(acidente) * getRiskFromTauTable(acidente)

                        novos_dados = pd.DataFrame([{
                            'DATAHORA': pd.to_datetime(f"{acidente['DATA']} {acidente['HORA']}"),
                            'CHUVA': dados_no_momento_do_acidente["chuva"],
                            'VENTO': dados_no_momento_do_acidente["vento"],
                            'RAJADA': dados_no_momento_do_acidente["rajada"],
                            'CODIGO_TEMPO': dados_no_momento_do_acidente["codigo_tempo"]
                        }])

                        # 1. Se o arquivo já existe, lê e junta os dados
                        if os.path.exists(fileWeather):
                            weatherAtual = pd.read_csv(fileWeather)
                            # Concatena o atual com os novos dados
                            weatherFinal = pd.concat([weatherAtual, novos_dados], ignore_index=True)
                        else:
                            # 2. Se não existe, o DataFrame final são apenas os novos dados
                            weatherFinal = novos_dados

                        # 3. Salva o resultado final de volta no arquivo (reescrevendo com o bloco completo)
                        weatherFinal.to_csv(fileWeather, index=False)

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

def calculateGravity(numLeve: int, numMedia: int, numGrave: int, numFatal: int, numVeiculos: int):
    PESO_ACIDENTE_FATAL = 13
    PESO_ACIDENTE_GRAVE = 5
    PESO_ACIDENTE_MEDIO = 2
    PESO_ACIDENTE_LEVE  = 1

    TAXA_BASE_ACIDENTE  = 1

    somaGravidadePonderada = \
        (PESO_ACIDENTE_LEVE  * numLeve ) + \
        (PESO_ACIDENTE_MEDIO * numMedia) + \
        (PESO_ACIDENTE_GRAVE * numGrave) + \
        (PESO_ACIDENTE_FATAL * numFatal)

    return somaGravidadePonderada + (TAXA_BASE_ACIDENTE * numVeiculos)

def getRiskFromTauTable(acidente: pd.DataFrame):
    resultado = TAUTABLE.loc[
        (TAUTABLE["CLASSE"] == acidente["CLASSE"]) & 
        (TAUTABLE["SUBCLASSE"] == acidente["SUBCLASSE"]), 
        "TAU"
    ]

    return resultado.values[0] if not resultado.empty else 0

def calculateFatorClimatico(clima: dict[str, any]):
    MAXIMO_DIA_SECO = 1.0
    VIES_RISCO_CHUVA = 0.5
    VIES_RISCO_MAX_CHUVA = 20.0

    return MAXIMO_DIA_SECO - (VIES_RISCO_CHUVA * min(MAXIMO_DIA_SECO, clima["chuva"] / VIES_RISCO_MAX_CHUVA))

def calculateRecencia(acidente: pd.DataFrame):
    data_comparar = datetime.strptime(acidente["date"], "%Y-%m-%d")
    hoje = datetime.today()
    diferenca_anos = (hoje.year - data_comparar.year - ((hoje.month, hoje.day) < (data_comparar.month, data_comparar.day)))

    return math.pow(math.e, -((math.log(2, math.e) / 3) * diferenca_anos))

