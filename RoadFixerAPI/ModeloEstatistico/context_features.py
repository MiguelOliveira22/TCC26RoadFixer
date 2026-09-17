"""Integra dados contextuais ao painel mensal de risco por quilômetro.

Todas as fontes externas são normalizadas para CSV antes da modelagem. Assim,
o modelo não fica amarrado ao formato (frequentemente variável) de um portal.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Iterable
import re

import pandas as pd
from dateutil.easter import easter


def _read(path: Path) -> pd.DataFrame:
    """Lê CSV em UTF-8 ou Latin-1, com vírgula ou ponto e vírgula."""
    for encoding in ("utf-8", "latin1"):
        try:
            return pd.read_csv(path, sep=None, engine="python", encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Não foi possível ler {path}")


def _column(data: pd.DataFrame, alternatives: Iterable[str]) -> str | None:
    lookup = {str(name).strip().upper(): name for name in data.columns}
    for name in alternatives:
        if name.upper() in lookup:
            return lookup[name.upper()]
    return None


def _month(value: pd.Series) -> pd.Series:
    return pd.to_datetime(value, dayfirst=True, errors="coerce").dt.to_period("M")


def _nearest_by_month(panel: pd.DataFrame, source: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Associa cada km ao contador/levantamento mais próximo no mesmo mês."""
    result = panel.copy()
    for column in columns:
        # NaN preserva o tipo numérico; pd.NA transformaria a coluna em object
        # e o GridSearch deixaria de reconhecê-la como variável.
        result[column] = float("nan")
    for period, indices in result.groupby("PERIODO").groups.items():
        locations = source[source["PERIODO"] == period]
        if locations.empty:
            continue
        distance = (result.loc[indices, "KM"].to_numpy()[:, None] - locations["KM"].to_numpy()).__abs__()
        nearest = distance.argmin(axis=1)
        result.loc[indices, columns] = locations.iloc[nearest][columns].to_numpy()
    return result


def add_traffic(panel: pd.DataFrame, path: Path | list[Path]) -> pd.DataFrame:
    """Adiciona volume total e percentual de pesados de SAT/pedágio.

    CSV normalizado: data, km, volume_total, veiculos_pesados (opcional), rodovia.
    """
    paths = path if isinstance(path, list) else [path]
    data = pd.concat([_read(item) for item in paths], ignore_index=True)
    day = _column(data, ("DATA", "DATE", "DATA_HORA"))
    km = _column(data, ("KM", "KM_SENSOR", "QUILOMETRO"))
    volume = _column(data, ("VOLUME_TOTAL", "TOTAL_VEICULOS", "FLUXO_TOTAL", "VOLUME"))
    heavy = _column(data, ("VEICULOS_PESADOS", "VOLUME_PESADOS", "PESADOS", "QTD_COMERCIAL"))
    motorcycle = _column(data, ("QTD_MOTO", "MOTOS"))
    passenger = _column(data, ("QTD_PASSEIO", "PASSEIO"))
    road = _column(data, ("RODOVIA", "RODOVIA_SIGLA"))
    if not all((day, km)) or not volume and not all((motorcycle, passenger, heavy)):
        raise ValueError("traffic.csv precisa ter data, km e volume_total; o arquivo diário ARTESP com QTD_* também é aceito.")
    # O arquivo diário da ARTESP contém toda a malha; este projeto analisa SP-330.
    if road:
        road_name = data[road].astype(str).str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
        data = data[road_name.eq("SP330")].copy()
    if data.empty:
        raise ValueError("Os arquivos de tráfego informados não possuem registros da SP-330.")
    if volume:
        total = pd.to_numeric(data[volume], errors="coerce")
    else:
        total = sum(pd.to_numeric(data[column], errors="coerce").fillna(0) for column in (motorcycle, passenger, heavy))
    traffic = pd.DataFrame({"PERIODO": _month(data[day]), "KM": pd.to_numeric(data[km], errors="coerce"),
                            "fluxo_total": total})
    traffic["fluxo_pesados"] = pd.to_numeric(data[heavy], errors="coerce") if heavy else 0
    traffic = traffic.dropna(subset=["PERIODO", "KM", "fluxo_total"])
    traffic["KM"] = traffic["KM"].round().astype(int)
    traffic = traffic.groupby(["PERIODO", "KM"], as_index=False).sum(numeric_only=True)
    traffic["percentual_pesados"] = (traffic["fluxo_pesados"] / traffic["fluxo_total"].clip(lower=1)).clip(0, 1)
    return _nearest_by_month(panel, traffic, ["fluxo_total", "fluxo_pesados", "percentual_pesados"])


def add_weather(panel: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Adiciona tempo mensal; use uma estação/grade representativa de cada trecho.

    CSV normalizado: data, precipitacao_mm, vento_kmh (opcional), visibilidade_km
    (opcional). Dados meteorológicos do próprio mês são defasados para não vazar.
    """
    data = _read(path)
    day = _column(data, ("DATA", "DATE"))
    rain = _column(data, ("PRECIPITACAO_MM", "PRECIPITATION_MM", "CHUVA_MM"))
    wind = _column(data, ("VENTO_KMH", "WIND_KMH"))
    visibility = _column(data, ("VISIBILIDADE_KM", "VISIBILITY_KM"))
    if not day or not rain:
        raise ValueError("weather.csv precisa ter data e precipitacao_mm.")
    weather = pd.DataFrame({"PERIODO": _month(data[day]), "chuva_mm": pd.to_numeric(data[rain], errors="coerce")})
    weather["vento_kmh"] = pd.to_numeric(data[wind], errors="coerce") if wind else pd.NA
    weather["visibilidade_km"] = pd.to_numeric(data[visibility], errors="coerce") if visibility else pd.NA
    weather = weather.dropna(subset=["PERIODO"]).groupby("PERIODO", as_index=False).agg(
        chuva_mm=("chuva_mm", "sum"), vento_kmh=("vento_kmh", "mean"), visibilidade_km=("visibilidade_km", "mean")
    )
    # Para previsão mensal, somente o tempo observado até o mês anterior entra.
    weather["PERIODO"] = weather["PERIODO"] + 1
    return panel.merge(weather, on="PERIODO", how="left")


def add_inmet_weather(panel: pd.DataFrame, inmet_dir: Path) -> pd.DataFrame:
    """Lê os CSVs horários do INMET já armazenados pelo projeto.

    Os arquivos do INMET têm oito linhas de metadados e codificação variável;
    precipitação e vento são agregados por mês e defasados um mês.
    """
    files = sorted(inmet_dir.glob("**/*.csv"))
    if not files:
        return panel
    frames = []
    for path in files:
        raw = pd.read_csv(path, sep=";", skiprows=8, encoding="latin1", low_memory=False)
        day = _column(raw, ("DATA", "Data"))
        rain = next((column for column in raw.columns if "PRECIP" in str(column).upper()), None)
        wind = next((column for column in raw.columns if "VENTO" in str(column).upper() and "VELOCIDADE" in str(column).upper()), None)
        if not day or not rain:
            continue
        values = pd.DataFrame({"PERIODO": pd.to_datetime(raw[day], format="%Y/%m/%d", errors="coerce").dt.to_period("M"), "chuva_mm": raw[rain]})
        values["chuva_mm"] = pd.to_numeric(values["chuva_mm"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
        values["chuva_mm"] = values["chuva_mm"].mask(values["chuva_mm"] < 0)
        values["vento_kmh"] = pd.to_numeric(raw[wind].astype(str).str.replace(",", ".", regex=False), errors="coerce") * 3.6 if wind else pd.NA
        frames.append(values)
    if not frames:
        return panel
    weather = pd.concat(frames, ignore_index=True).dropna(subset=["PERIODO"])
    weather = weather.groupby("PERIODO", as_index=False).agg(chuva_mm=("chuva_mm", "sum"), vento_kmh=("vento_kmh", "mean"))
    weather["PERIODO"] = weather["PERIODO"] + 1
    return panel.merge(weather, on="PERIODO", how="left")


def add_speed(panel: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Adiciona velocidade e índice de congestionamento por trecho.

    CSV normalizado: data, km, velocidade_media_kmh, velocidade_livre_kmh
    (a última é opcional). A fonte pode ser a concessionária ou fornecedor de
    dados de mobilidade, desde que a licença permita uso analítico.
    """
    data = _read(path)
    day = _column(data, ("DATA", "DATE", "DATA_HORA"))
    km = _column(data, ("KM", "KM_SENSOR", "QUILOMETRO"))
    speed = _column(data, ("VELOCIDADE_MEDIA_KMH", "VELOCIDADE_KMH", "SPEED_KMH"))
    free_speed = _column(data, ("VELOCIDADE_LIVRE_KMH", "FREE_FLOW_KMH"))
    if not all((day, km, speed)):
        raise ValueError("speed.csv precisa ter data, km e velocidade_media_kmh.")
    result = pd.DataFrame({"PERIODO": _month(data[day]), "KM": pd.to_numeric(data[km], errors="coerce"),
                           "velocidade_media_kmh": pd.to_numeric(data[speed], errors="coerce")})
    result["velocidade_livre_kmh"] = pd.to_numeric(data[free_speed], errors="coerce") if free_speed else pd.NA
    result = result.dropna(subset=["PERIODO", "KM", "velocidade_media_kmh"])
    result["KM"] = result["KM"].round().astype(int)
    result = result.groupby(["PERIODO", "KM"], as_index=False).mean(numeric_only=True)
    if "velocidade_livre_kmh" in result and result["velocidade_livre_kmh"].notna().any():
        result["indice_congestionamento"] = (1 - result["velocidade_media_kmh"] / result["velocidade_livre_kmh"].clip(lower=1)).clip(0, 1)
    else:
        result["indice_congestionamento"] = pd.NA
    # Como chuva, a velocidade observada é histórica; a linha seguinte a usa.
    result["PERIODO"] = result["PERIODO"] + 1
    return _nearest_by_month(panel, result, ["velocidade_media_kmh", "velocidade_livre_kmh", "indice_congestionamento"])


def add_works(panel: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Marca obras ativas. CSV: inicio, fim, km_inicial, km_final, intensidade."""
    works = _read(path)
    begin, end = _column(works, ("INICIO", "DATA_INICIO")), _column(works, ("FIM", "DATA_FIM"))
    start_km, end_km = _column(works, ("KM_INICIAL", "KM_INICIO")), _column(works, ("KM_FINAL", "KM_FIM"))
    intensity = _column(works, ("INTENSIDADE", "IMPACTO"))
    if not all((begin, end, start_km, end_km)):
        raise ValueError("works.csv precisa ter inicio, fim, km_inicial e km_final.")
    result = panel.copy()
    result["obra_ativa"] = 0.0
    for _, work in works.iterrows():
        months = pd.period_range(pd.to_datetime(work[begin]), pd.to_datetime(work[end]), freq="M")
        mask = result["PERIODO"].isin(months) & result["KM"].between(float(work[start_km]), float(work[end_km]))
        result.loc[mask, "obra_ativa"] = float(work[intensity]) if intensity and pd.notna(work[intensity]) else 1.0
    return result


def add_infrastructure(panel: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Aplica atributos estáveis por intervalo.

    CSV: km_inicial, km_final, n_faixas, limite_velocidade_kmh, declive_percent,
    raio_curva_m, iluminacao, acostamento_m, acessos_por_km (todos opcionais após
    os dois km).
    """
    infra = _read(path)
    start, end = _column(infra, ("KM_INICIAL", "KM_INICIO")), _column(infra, ("KM_FINAL", "KM_FIM"))
    if not start or not end:
        raise ValueError("infrastructure.csv precisa ter km_inicial e km_final.")
    result = panel.copy()
    allowed = ("N_FAIXAS", "LIMITE_VELOCIDADE_KMH", "DECLIVE_PERCENT", "RAIO_CURVA_M", "ILUMINACAO", "ACOSTAMENTO_M", "ACESSOS_POR_KM")
    columns = [column for column in allowed if column in infra.columns]
    for column in columns:
        result[column.lower()] = pd.NA
    for _, segment in infra.iterrows():
        mask = result["KM"].between(float(segment[start]), float(segment[end]))
        for column in columns:
            result.loc[mask, column.lower()] = segment[column]
    return result


def add_artesp_infrastructure(panel: pd.DataFrame, malha_path: Path, access_path: Path) -> pd.DataFrame:
    """Extrai atributos úteis dos XLSX de Malha e Acessos da ARTESP.

    A malha informa tipo de pista e administração. O cadastro de acessos é
    convertido em densidade por km e indicadores de condição/conformidade.
    """
    result = panel.copy()
    malha = pd.read_excel(malha_path, sheet_name="MALHA_RODOVIARIA_SP")
    road = _column(malha, ("RODOVIA",))
    malha = malha[malha[road].astype(str).str.replace(r"[^A-Z0-9]", "", regex=True).eq("SP330")]
    result["pista_dupla"] = 0.0
    result["trecho_planejado"] = 0.0
    start, end = _column(malha, ("KM_INICIAL",)), _column(malha, ("KM_FINAL",))
    track, administration = _column(malha, ("PISTA_ATUAL",)), _column(malha, ("ADMINISTRACAO",))
    for _, segment in malha.iterrows():
        mask = result["KM"].between(float(segment[start]), float(segment[end]))
        result.loc[mask, "pista_dupla"] = float(str(segment[track]).upper() == "DUPLA") if track else 0.0
        result.loc[mask, "trecho_planejado"] = float(str(segment[track]).upper() == "PLANEJADA") if track else 0.0
        if administration:
            result.loc[mask, "administracao_artesp"] = float(str(segment[administration]).upper() == "ARTESP")

    access = pd.read_excel(access_path, dtype=str)
    road = _column(access, ("RODOVIA",))
    access = access[access[road].astype(str).str.replace(r"[^A-Z0-9]", "", regex=True).eq("SP330")].copy()
    code = next((column for column in access.columns if "ACESSO" in str(column).upper() and "C" in str(column).upper()), None)
    km = _column(access, ("KM",))
    if not code or not km:
        return result

    def parse_access_km(row: pd.Series) -> float | None:
        digits = re.sub(r"\D", "", str(row[km]))
        match = re.search(r"SP330-(\d+)-", str(row[code]).upper())
        if not digits or not match:
            return None
        whole = match.group(1)
        if digits.startswith(whole):
            fraction = digits[len(whole):]
            return float(whole + ("." + fraction if fraction else ""))
        return float(digits)

    access["KM_NORMALIZADO"] = access.apply(parse_access_km, axis=1)
    access = access.dropna(subset=["KM_NORMALIZADO"])
    access["KM"] = access["KM_NORMALIZADO"].round().astype(int)
    authorized = next((column for column in access.columns if "AUTORIZADO" in str(column).upper() and "PROJETO" not in str(column).upper()), None)
    conforms = next((column for column in access.columns if "ATENDE" in str(column).upper() and "NORMA" in str(column).upper()), None)
    condition = next((column for column in access.columns if "CONSERVA" in str(column).upper()), None)
    activity = next((column for column in access.columns if "ATIVIDADE" in str(column).upper()), None)
    access["acessos_nao_autorizados"] = (~access[authorized].astype(str).str.upper().str.startswith("SIM")).astype(int) if authorized else 0
    access["acessos_nao_conformes"] = (~access[conforms].astype(str).str.upper().str.startswith("SIM")).astype(int) if conforms else 0
    access["acessos_conservacao_ruim"] = access[condition].astype(str).str.upper().str.contains("RUIM", na=False).astype(int) if condition else 0
    access["acessos_comerciais"] = access[activity].astype(str).str.upper().str.startswith("A").astype(int) if activity else 0
    counts = access.groupby("KM", as_index=False).agg(
        acessos_por_km=("KM", "size"), acessos_nao_autorizados=("acessos_nao_autorizados", "sum"),
        acessos_nao_conformes=("acessos_nao_conformes", "sum"), acessos_conservacao_ruim=("acessos_conservacao_ruim", "sum"),
        acessos_comerciais=("acessos_comerciais", "sum"),
    )
    return result.merge(counts, on="KM", how="left")


def add_calendar(panel: pd.DataFrame) -> pd.DataFrame:
    """Inclui dias de fim de semana e feriados federais brasileiros por mês."""
    result = panel.copy()
    dates = pd.date_range(result["PERIODO"].min().start_time, result["PERIODO"].max().end_time, freq="D")
    holidays = set()
    for year in sorted(set(dates.year)):
        easter_day = easter(year)
        holidays.update({date(year, 1, 1), date(year, 4, 21), date(year, 5, 1), date(year, 9, 7),
                         date(year, 10, 12), date(year, 11, 2), date(year, 11, 15), date(year, 11, 20), date(year, 12, 25),
                         easter_day - timedelta(days=48), easter_day - timedelta(days=2), easter_day + timedelta(days=60)})
    calendar = pd.DataFrame({"date": dates})
    calendar["PERIODO"] = calendar["date"].dt.to_period("M")
    calendar["fim_de_semana"] = calendar["date"].dt.dayofweek.ge(5).astype(int)
    calendar["feriado"] = calendar["date"].dt.date.isin(holidays).astype(int)
    calendar = calendar.groupby("PERIODO", as_index=False)[["fim_de_semana", "feriado"]].sum()
    return result.merge(calendar, on="PERIODO", how="left")


def enrich(panel: pd.DataFrame, external_dir: Path | None, inmet_dir: Path | None = None) -> pd.DataFrame:
    """Carrega apenas os arquivos existentes; ausências não interrompem o modelo."""
    result = add_calendar(panel)
    if not external_dir:
        if inmet_dir:
            result = add_inmet_weather(result, inmet_dir)
        return result
    # O CSV diário baixado da ARTESP também pode ficar em raw/ sem renomeação.
    traffic_path = external_dir / "traffic.csv"
    if not traffic_path.exists():
        raw_files = sorted((external_dir / "raw").glob("contagem_diaria_*.csv")) if (external_dir / "raw").exists() else []
        if raw_files:
            result = add_traffic(result, raw_files)
    malha_path, access_path = external_dir / "raw" / "cci_malha_rodoviaria_sp.xlsx", external_dir / "raw" / "acessos_rodoviarios.xlsx"
    if malha_path.exists() and access_path.exists():
        result = add_artesp_infrastructure(result, malha_path, access_path)
    sources = (("traffic.csv", add_traffic), ("weather.csv", add_weather), ("speed.csv", add_speed),
               ("works.csv", add_works), ("infrastructure.csv", add_infrastructure))
    for filename, loader in sources:
        path = external_dir / filename
        if path.exists():
            result = loader(result, path)
    if not (external_dir / "weather.csv").exists() and inmet_dir:
        result = add_inmet_weather(result, inmet_dir)
    return result
