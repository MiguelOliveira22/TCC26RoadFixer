import pandas as pd
import requests
from io import StringIO
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import re
import os
import ModeloEstatistico.core.riskCalculations as calc

BASE_DIR = Path(__file__).resolve().parent

def prepararPastas(ano):
    pastaData = BASE_DIR / "data" / str(ano)
    pastaWeather = BASE_DIR / "weather-data" / str(ano)

    pastaData.mkdir(parents=True, exist_ok=True)
    pastaWeather.mkdir(parents=True, exist_ok=True)

    return pastaData, pastaWeather

# ========================================================
# FUNÇÕES DE NORMALIZAÇÃO DA ARTESP
# ========================================================
def normalizar_classe(s):
    if pd.isna(s):
        return "NÃO INFORMADO"
    s = s.upper().strip()
    if re.search(r"OBJETO LAN.ADO", s):
        return "OBJETO LANÇADO CONTRA O VEÍCULO"
    return s

def normalizar_subclasse(s):
    if pd.isna(s):
        return "NÃO INFORMADO"
    s = s.upper().strip()
    
    regras = [
        (r"DEFENSA|BARREIRA|SUBMARINO", "CHOQUE-DEFENSA/BARREIRA"),
        (r"DRENAGEM", "CHOQUE-ELEMENTO DE DRENAGEM"),
        (r"TALUDE|BARRANCO|CORTE", "CHOQUE-TALUDE/BARRANCO"),
        (r"MEIO.?FIO|CALÇAMENTO", "CHOQUE-MEIO FIO"),
        (r"ÁRVORE|ARVORE", "CHOQUE-ÁRVORE"),
        (r"POSTE", "CHOQUE-POSTE"),
        (r"BURACO", "CHOQUE-BURACO"),
        (r"OBJETO.*PISTA|OBJETO SOBRE A VIA|VEÍCULO PARADO NA PISTA", "CHOQUE-OBJETO NA PISTA"),
        (r"VEÍCULO PARADO NO ACOSTAMENTO", "CHOQUE-VEÍCULO PARADO NO ACOSTAMENTO"),
        (r"OAE|PILAR|VIADUTO|PONTE", "CHOQUE-OAE (PONTE/VIADUTO)"),
        (r"PRAÇA|CABINE|CANCELA|PEDÁGIO", "CHOQUE-PRAÇA DE PEDÁGIO"),
        (r"SINALIZAÇÃO|EQUIPAMENTO|PAINEL", "CHOQUE-SINALIZAÇÃO/EQUIPAMENTO"),
        (r"CERCA|ALAMBRADO|MOURÃO", "CHOQUE-CERCAS/ALAMBRADOS"),
        (r"EDIFICAÇÃO|ILHA|MATACÃO|OUTROS|NÃO IDENTIF", "CHOQUE-OUTROS"),
        (r"^FRONTAL$|COLIS.O-FRONTAL", "COLISÃO-FRONTAL"),
        (r"^TRASEIRA$|COLIS.O-TRASEIRA", "COLISÃO-TRASEIRA"),
        (r"^LATERAL$|COLIS.O-LATERAL", "COLISÃO-LATERAL"),
        (r"^TRANSVERSAL$|COLIS.O-TRANSVERSAL", "COLISÃO-TRANSVERSAL"),
        (r"^TOMBAMENTO$", "TOMBAMENTO"),
        (r"TOMBAMENTO-MOTO", "TOMBAMENTO-MOTO"),
        (r"TOMBAMENTO.*PESAD", "TOMBAMENTO-VEÍCULO PESADO"),
        (r"TOMBAMENTO-BICICLETA", "TOMBAMENTO-BICICLETA"),
        (r"^CAPOTAMENTO$", "CAPOTAMENTO"),
        (r"^ENGAVETAMENTO$", "ENGAVETAMENTO"),
        (r"SUICID|SUICÍD", "ATROP. PEDESTRE-SUICÍDIO"),
        (r"CICLISTA", "ATROP. PEDESTRE-CICLISTA"),
        (r"ATROP\.? PEDESTRE|DE PEDESTRE|PEDESTRE USUÁRIO", "ATROP. PEDESTRE-OUTROS"),
        (r"ANIMAL.*SILVESTRE.*GRANDE", "ATROP. ANIMAL-SILVESTRE GRANDE"),
        (r"ANIMAL.*SILVESTRE.*M.DIO", "ATROP. ANIMAL-SILVESTRE MÉDIO"),
        (r"ANIMAL.*SILVESTRE.*PEQUENO", "ATROP. ANIMAL-SILVESTRE PEQUENO"),
        (r"ANIMAL.*DOM.STICO.*GRANDE", "ATROP. ANIMAL-DOMÉSTICO GRANDE"),
        (r"ANIMAL.*DOM.STICO.*M.DIO", "ATROP. ANIMAL-DOMÉSTICO MÉDIO"),
        (r"ANIMAL.*DOM.STICO.*PEQUENO", "ATROP. ANIMAL-DOMÉSTICO PEQUENO"),
        (r"ANIMAL", "ATROP. ANIMAL-OUTROS"),
        (r"^QUEDA-MOTO$", "QUEDA-MOTO"),
        (r"^QUEDA-CICLISTA$", "QUEDA-CICLISTA"),
        (r"RIBANCEIRA|EM RIBANCEIRA", "QUEDA-RIBANCEIRA/OAE"),
        (r"QUEDA-CARGA", "QUEDA-CARGA"),
        (r"^QUEDA$|TABLUDE", "QUEDA-OUTROS"),
        (r"LAN.ADO", "OBJETO LANÇADO CONTRA O VEÍCULO"),
        (r"INC.NDIO", "INCÊNDIO"),
        (r"SA.DA DE PISTA", "SAÍDA DE PISTA"),
    ]
    
    for padrao, categoria in regras:
        if re.search(padrao, s):
            return categoria
    
    return "OUTROS/NÃO CLASSIFICADO"

# ========================================================
# ATUALIZAÇÃO ARTESP E CLIMA
# ========================================================
def atualizarARTESP():
    ano = datetime.now().year
    pastaData, _ = prepararPastas(ano)

    URL = (
        f"https://dadosabertos.artesp.sp.gov.br/dataset/"
        f"5e3af2a0-3b6a-4ee6-8556-b59b5d813ffc/resource/"
        f"7aee242c-8be1-43ea-a2e7-d9525ec926d9/download/"
        f"acidentes_{ano}.csv"
    )

    arquivoCompleto = pastaData / f"{ano}.csv"
    arquivoAnhanguera = pastaData / f"p{ano}.csv"

    try:
        print(f"[ARTESP] Baixando dados de {ano}...")
        response = requests.get(URL, timeout=60)
        response.raise_for_status()

        data = pd.read_csv(StringIO(response.content.decode("utf-8")))

        if "CLASSE" in data.columns:
            data["CLASSE"] = data["CLASSE"].apply(normalizar_classe)
        if "SUBCLASSE" in data.columns:
            data["SUBCLASSE"] = data["SUBCLASSE"].apply(normalizar_subclasse)

        data["RODOVIA"] = data["RODOVIA"].astype(str).str.upper().str.strip()
        data.to_csv(arquivoCompleto, index=False, encoding="utf-8")

        anhanguera = data[data["RODOVIA"].str.contains("330", na=False)].copy()

        if "DATA" in anhanguera.columns:
            anhanguera["DATA"] = pd.to_datetime(anhanguera["DATA"], errors="coerce")
            if "HORA" in anhanguera.columns:
                anhanguera = anhanguera.sort_values(["DATA", "HORA"])

        colunas_remover = ["_id", "VITIMAS_SEM_INFO", "VITIMA_ILESA", "VISIBILIDADE", "CONDICAO_METERIOLOGICA"]
        anhanguera = anhanguera.drop(columns=[col for col in colunas_remover if col in anhanguera.columns])

        anhanguera.to_csv(arquivoAnhanguera, index=False, encoding="utf-8")

        print(f"[ARTESP] {len(anhanguera)} acidentes da Anhanguera processados e salvos.")
        return True

    except Exception as e:
        print(f"[ARTESP] Erro: {e}")
        return False


def atualizarSistema():
    ano = datetime.now().year

    print(f"\n===== ATUALIZAÇÃO DO SISTEMA {ano} =====")
    prepararPastas(ano)

    print("\n===== Realizando o Calculo dos Riscos =====")
    calc.calcAccidents()

    artesp_ok = atualizarARTESP()

    if artesp_ok:
        print("[UPDATE] Dados atualizados com sucesso.")
        return True

    print("[UPDATE] Houve erro na atualização.")
    return False

async def atualizacaoDiaria():
    while True:
        try:
            print("[SCHEDULER] Executando atualização...")
            await asyncio.to_thread(atualizarSistema)
        except Exception as e:
            print(f"[SCHEDULER] Erro na atualização: {e}")

        agora = datetime.now()
        proxima = (agora + timedelta(days=1)).replace(hour=3, minute=0, second=0, microsecond=0)
        espera = (proxima - datetime.now()).total_seconds()

        print(f"[SCHEDULER] Próxima atualização: {proxima.strftime('%d/%m/%Y %H:%M:%S')}")
        await asyncio.sleep(espera)

def iniciarAtualizacao():
    return asyncio.create_task(atualizacaoDiaria())