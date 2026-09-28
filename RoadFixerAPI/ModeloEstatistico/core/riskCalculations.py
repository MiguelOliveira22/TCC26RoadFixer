<<<<<<< Updated upstream
from datetime import datetime
=======
"""Fallback histórico local para o painel de risco."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
>>>>>>> Stashed changes
from pathlib import Path

import pandas as pd

<<<<<<< Updated upstream
filepath = Path("./ModeloEstatistico/data")
filepathRisk = Path("./API/content/accident-history")

TAUTABLE = pd.read_csv(str(filepath) + "/tau.csv", encoding="utf-8")

def calcAccidents():
    directory = Path(filepath, "accidents")
=======

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "accidents" / "processed"
TAU_PATH = BASE_DIR / "ModeloEstatistico" / "data_tau" / "tau.csv"
RISK_PATH = BASE_DIR / "API" / "content" / "accident-history" / "risk" / "savedData.json"

>>>>>>> Stashed changes

def calculateGravity(numLeve: float, numMedia: float, numGrave: float, numFatal: float, numVeiculos: float = 0) -> float:
    """Peso de severidade: 1, 2, 5 e 13; veículos não alteram a gravidade."""
    light, moderate, serious, fatal = (max(0.0, float(value or 0)) for value in (numLeve, numMedia, numGrave, numFatal))
    return 1.0 + light + 2.0 * moderate + 5.0 * serious + 13.0 * fatal

<<<<<<< Updated upstream
        for file_path in directory.iterdir():
            print(f"Lendo arquivo: {file_path.name}")
=======

def calculateFatorClimatico(clima: dict[str, object]) -> float:
    """Mantido por compatibilidade: chuva só aumenta, nunca reduz, o índice."""
    try:
        rainfall = max(0.0, float(clima.get("CHUVA", clima.get("chuva", 0))))
    except (TypeError, ValueError):
        rainfall = 0.0
    return 1.0 + 0.5 * min(1.0, rainfall / 20.0)
>>>>>>> Stashed changes


def calculateRecencia(acidente: dict[str, object]) -> float:
    value = str(acidente.get("DATA", acidente.get("date")))
    occurred = datetime.strptime(value.split("T")[0].split(" ")[0], "%Y-%m-%d").date()
    years = (datetime.now().date() - occurred).days / 365.2425
    return math.exp(-math.log(2) * years / 3.0)


<<<<<<< Updated upstream
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

                        newData[acidente["KM"]] += calculateGravity(acidente["VI"], acidente["VL"], acidente["VM"], acidente["VG"], acidente["VF"]) * calculateFatorClimatico(dados_no_momento_do_acidente) * calculateRecencia(acidente) * getRiskFromTauTable(acidente)

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
=======
def calcAccidents() -> dict[str, object]:
    """Gera fallback local no mesmo contrato publicado pela API."""
    files = sorted(DATA_DIR.glob("p*.csv"))
    if not files:
        raise FileNotFoundError(f"Nenhum acidente processado em {DATA_DIR}")
    tau = pd.read_csv(TAU_PATH, encoding="utf-8")
    frames = []
    required = {"DATA", "KM", "VITIMA_LEVE", "VITIMA_MODERADA", "VITIMA_GRAVE", "VITIMA_FATAL"}
    for path in files:
        data = pd.read_csv(path, encoding="utf-8")
        if required.difference(data.columns):
            continue
        data["KM"] = pd.to_numeric(data["KM"].astype(str).str.replace(",", ".", regex=False), errors="coerce").round()
        for column in required - {"DATA", "KM"}:
            data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
        data = data.dropna(subset=["KM"]).copy()
        data["score"] = 1 + data["VITIMA_LEVE"] + 2 * data["VITIMA_MODERADA"] + 5 * data["VITIMA_GRAVE"] + 13 * data["VITIMA_FATAL"]
        if {"CLASSE", "SUBCLASSE"}.issubset(data.columns):
            data = data.merge(tau, on=["CLASSE", "SUBCLASSE"], how="left")
            data["score"] *= data["TAU"].fillna(1.0).clip(lower=0)
        data["score"] *= data["DATA"].map(lambda value: calculateRecencia({"DATA": value}))
        frames.append(data[["KM", "score"]])
    if not frames:
        raise ValueError("Nenhum arquivo possui as colunas mínimas de vítimas.")
>>>>>>> Stashed changes

    score = pd.concat(frames).groupby("KM")["score"].sum()
    raw = pd.Series(0.0, index=range(int(score.index.max()) + 1))
    raw.loc[score.index.astype(int)] = score.to_numpy()
    ceiling = float(raw.quantile(0.95))
    risk = raw.clip(upper=ceiling).div(ceiling).mul(10) if ceiling > 0 else raw
    payload = {
        "last_update": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "periodo_previsto": None,
        "metodo": "fallback histórico ponderado; previsão temporal indisponível",
        "risk": risk.round(3).tolist(),
    }
    RISK_PATH.parent.mkdir(parents=True, exist_ok=True)
    RISK_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "fallback histórico atualizado", "km": len(risk)}
