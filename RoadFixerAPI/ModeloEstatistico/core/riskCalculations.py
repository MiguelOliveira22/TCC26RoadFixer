from datetime import datetime

import requests
import pandas as pd
import time
import statistics
import math

from ...database import get_database


def calcAccidents():
    database = get_database()
    countFilesData = 0
    savedData = database.get_risk()
    tau_table = database.load_tau()
    newData = [0] * len(savedData["risk"])

    for source_file in database.accident_sources():
        weatherAtual = database.load_weather(source_file)
        if weatherAtual is not None:
            weatherAtual["DATAHORA"] = pd.to_datetime(weatherAtual["DATAHORA"], format="mixed")
        print(f"Lendo acidentes do DuckDB: {source_file}")
        data = database.load_accidents(source_file)

        # Evita erro caso o arquivo lido esteja sem registros
        if data.empty:
            continue

        countFilesData += 1

        # 1. Monta as colunas derivadas direto no DataFrame (bem mais
        # rápido do que fazer um for linha a linha em Python puro)

        # Extrai apenas a data, sem hora (ex: "2026-01-01T00:00:00" -> "2026-01-01")
        data["DATA"] = data["DATA"].astype(str).str.split("T").str[0].str.split(" ").str[0]

        # Extrai apenas o número da hora (ex: "06:30:00" -> 6)
        # data["HORA"] = data["HORA"].astype(str).str.split(":").str[0].astype(int)

        # KM: troca vírgula por ponto (padrão BR -> padrão numérico) e arredonda
        data["KM"] = (
            data["KM"].astype(str).str.replace(",", ".", regex=False).astype(float).round().astype(int)
        )

        data = data[data["KM"] >= 0]
        if not data.empty and int(data["KM"].max()) >= len(newData):
            newData.extend([0] * (int(data["KM"].max()) + 1 - len(newData)))

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
                for acidente in batch:
                    dados_no_momento_do_acidente = weatherAtual[(pd.to_datetime(weatherAtual["DATAHORA"]) == pd.to_datetime(f"{acidente['DATA']} {acidente['HORA']}"))].iloc[0].to_dict()
                    newData[acidente["KM"]] += calculateGravity(acidente["VL"], acidente["VM"], acidente["VG"], acidente["VF"], acidente["NUMVEÍCULOS"]) * calculateFatorClimatico(dados_no_momento_do_acidente) * calculateRecencia(acidente) * getRiskFromTauTable(acidente, tau_table)
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
                        response = requests.get(url, params=params, timeout=60)
                    except requests.exceptions.RequestException as e:
                        print(f"Erro ao chamar open-meteo no lote {b}: {e} (tentativa {tentativa + 1}/{MAX_RETRIES})")
                        time.sleep(2 ** tentativa)  # backoff exponencial: 1s, 2s, 4s...
                        continue

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
                new_weather_frames = []
                for acidente, meteo_ponto in zip(batch, meteo_list):
                    hourly = meteo_ponto["hourly"]

                    # timestamp exato do acidente, no mesmo formato que vem em hourly["time"]
                    hora_str = acidente['HORA'].split(':')[0]  # pega só "01" de "01:36:00"
                    timestamp_alvo = f"{acidente['DATA']}T{hora_str}:00"

                    try:
                        h_idx = hourly["time"].index(timestamp_alvo)
                    except ValueError:
                        print(f"Timestamp {timestamp_alvo} não encontrado no retorno do open-meteo")
                        continue

                    dados_no_momento_do_acidente = {
                        "HORA": hourly["time"][h_idx],
                        "CHUVA": hourly["precipitation"][h_idx],
                        "VENTO": hourly["wind_speed_10m"][h_idx],
                        "RAJADA": hourly["wind_gusts_10m"][h_idx],
                        "CODIGO_TEMPO": hourly["weather_code"][h_idx],
                    }

                    newData[acidente["KM"]] += calculateGravity(acidente["VL"], acidente["VM"], acidente["VG"], acidente["VF"], acidente["NUMVEÍCULOS"]) * calculateFatorClimatico(dados_no_momento_do_acidente) * calculateRecencia(acidente) * getRiskFromTauTable(acidente, tau_table)
                    novos_dados = pd.DataFrame([{
                        'DATAHORA': pd.to_datetime(f"{acidente['DATA']} {acidente['HORA']}"),
                        'CHUVA': dados_no_momento_do_acidente["CHUVA"],
                        'VENTO': dados_no_momento_do_acidente["VENTO"],
                        'RAJADA': dados_no_momento_do_acidente["RAJADA"],
                        'CODIGO_TEMPO': dados_no_momento_do_acidente["CODIGO_TEMPO"]
                    }])
                    print(novos_dados)

                    new_weather_frames.append(novos_dados)

                if new_weather_frames:
                    frames = ([weatherAtual] if weatherAtual is not None else []) + new_weather_frames
                    weatherAtual = pd.concat(frames, ignore_index=True)
                    weatherAtual["DATAHORA"] = pd.to_datetime(weatherAtual["DATAHORA"], format="mixed")
                    database.save_weather(source_file, weatherAtual)

    # O índice e a data são publicados juntos, após concluir o cálculo.
    if countFilesData > 0 and newData:
        newData = [value / countFilesData for value in newData]
        media = sum(newData) / len(newData)
        desvio_padrao = statistics.pstdev(newData)
        risk = [
            10 / (1 + math.exp(-((value - media) / desvio_padrao)))
            if desvio_padrao else 0.0
            for value in newData
        ]
        database.save_risk({
            "last_update": datetime.today().strftime("%Y-%m-%d"),
            "risk": risk,
        })

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

def getRiskFromTauTable(acidente: pd.DataFrame, tau_table=None):
    if tau_table is None:
        tau_table = get_database().load_tau()
    resultado = tau_table.loc[
        (tau_table["CLASSE"] == acidente["CLASSE"]) &
        (tau_table["SUBCLASSE"] == acidente["SUBCLASSE"]),
        "TAU"
    ]

    return resultado.values[0] if not resultado.empty else 0

def calculateFatorClimatico(clima: dict[str, object]):
    """Retorna um multiplicador de risco: chuva nunca reduz o risco histórico."""
    FATOR_DIA_SECO = 1.0
    AUMENTO_MAXIMO_POR_CHUVA = 0.5
    CHUVA_REFERENCIA_MM = 20.0

    chuva_mm = max(0.0, float(clima.get("CHUVA", 0) or 0))
    intensidade_normalizada = min(1.0, chuva_mm / CHUVA_REFERENCIA_MM)
    return FATOR_DIA_SECO + (AUMENTO_MAXIMO_POR_CHUVA * intensidade_normalizada)

def calculateRecencia(acidente: pd.DataFrame):
    data_comparar = datetime.strptime(acidente["DATA"], "%Y-%m-%d")
    hoje = datetime.today()
    diferenca_anos = (hoje.year - data_comparar.year - ((hoje.month, hoje.day) < (data_comparar.month, data_comparar.day)))

    return math.pow(math.e, -((math.log(2, math.e) / 3) * diferenca_anos))
