import styles from "./EstatisticasPage.module.css";
import 'leaflet/dist/leaflet.css';
import DataCollection from "../components/DataCollection";
import Graph from "../components/Graph";
import Map from "../components/Map";
import { useEffect, useState } from "react";
import { apiPath } from "../Constants";

async function getReports() {
  const res = await fetch(apiPath + "accidentHistory");
  const data = await res.json();
  const formatted = data.content.map((valor) => ({ id: valor.id, data: valor.data }));
  return formatted;
}

async function getRiskData() {
  const res = await fetch(apiPath + "riskData");
  if (!res.ok) throw new Error(`Falha ao carregar risco: HTTP ${res.status}`);
  const data = await res.json();
  const formatted = (Array.isArray(data.risk) ? data.risk : []).map((valor, index) => ({ KM: String(index), risco: valor }));
  return { formatted, metadata: data, details: Array.isArray(data.trechos) ? data.trechos : [] };
}

async function getPredictionData() {
  const res = await fetch(apiPath + "predictionData");
  const data = await res.json();
  return {
    period: data.period,
    values: (data.predictions ?? []).map((valor) => ({
      KM: String(valor.KM),
      risco: valor.risco,
    })),
  };
}

export default function EstatisticasPage() {
  const [reports, setReports] = useState(null);
  const [riskData, setRiskData] = useState([]);
  const [predictionData, setPredictionData] = useState([]);
  const [predictionPeriod, setPredictionPeriod] = useState(null);

  // Ponto central padrão para manter a alinhamento do mapa
  const defaultCenter = [-22.92506, -47.08692];
  const marks = [{ position: defaultCenter, information: "Rodovia Anhanguera (SP-330)" }];

  useEffect(() => {
    const loadData = async () => {
      try {
        const [reportsData, risk, prediction] = await Promise.all([
          getReports(),
          getRiskData(),
          getPredictionData(),
        ]);
        setReports(reportsData);
        setRiskData(risk);
        setPredictionData(prediction.values);
        setPredictionPeriod(prediction.period);
      } catch (error) {
        console.error("Erro ao carregar dados das estatísticas:", error);
      }
    };
    loadData();
  }, []);

  // Monta { KM, valor, risco } para o tipo atual. "risco" é a versão 0–10 usada nas cores.
  const dadosAtuais = useMemo(() => {
    const tipo = TIPOS_DADO.find((t) => t.label === tipoDado);
    const valores = series[tipoDado] ?? [];
    const max = tipo?.escalaFixa ? 10 : Math.max(...valores, 0);

    return valores.map((valor, i) => ({
      KM: String(i),
      valor,
      risco: max > 0 ? Math.min((valor / max) * 10, 10) : 0,
    }));
  }, [tipoDado, series]);

  const tipoAtual = TIPOS_DADO.find((t) => t.label === tipoDado);

  const handleTipoChange = (e) => {
    const valor = e.target.value;
    setInputValue(valor);
    if (series[valor]) setTipoDado(valor); // só aceita opções com dados carregados
  };

  return (
    <div className={styles.pageWrapper}>
      {/* SEÇÃO 1: ÍNDICE HISTÓRICO */}
      <section className={styles.section}>
        <div className={styles.header}>
          <p className={styles.kicker}>PREVISÃO PARA TRIAGEM HUMANA</p>
          <h2 className={styles.title}>
            ÍNDICE DE RISCO <span className={styles.highlight}>HISTÓRICO</span>
          </h2>
          <p className={styles.subtitle}>
            Índice heurístico atualizado diariamente a partir dos acidentes históricos e das condições climáticas.
          </p>
        </div>

        <div className={styles.seletorDado}>
          <label htmlFor="tipoDado">Dado exibido</label>
          <input
            id="tipoDado"
            list="options"
            value={inputValue}
            onChange={handleTipoChange}
            onFocus={() => setInputValue("")}
            onBlur={() => setInputValue(tipoDado)}
            placeholder="Selecione o tipo de dado"
          />
          <datalist id="options">
            {TIPOS_DADO.filter((t) => series[t.label]).map((t) => (
              <option key={t.label} value={t.label} />
            ))}
          </datalist>
          {!tipoAtual?.escalaFixa && (
            <small>Cores relativas ao maior valor da via para este dado.</small>
          )}
        </div>

        <div className={styles.dataGrid}>
          <div className={styles.mapCard}>
            <Map risk={dadosAtuais} label={tipoDado} marks={marks} center={defaultCenter} zoom={10} />
          </div>
          <div className={styles.graphCard}>
            <Graph data={dadosAtuais} label={tipoDado} escalaFixa={!!tipoAtual?.escalaFixa} />
          </div>
        </div>
      </section>

      {/* SEÇÃO 2: PREVISÃO DO MODELO */}
      <section className={styles.section}>
        <div className={styles.header}>
          <p className={styles.kicker}>PREVISÃO DO EXTRA TREES</p>
          <h2 className={styles.title}>
            RANKING DE RISCO <span className={styles.highlight}>PREVISTO</span>
          </h2>
          <p className={styles.subtitle}>
            {predictionPeriod
              ? `Severidade esperada por km para ${predictionPeriod}, usando somente informações anteriores.`
              : "A previsão será exibida após a primeira execução do modelo."}
          </p>
        </div>

        <div className={styles.dataGrid}>
          <div className={styles.mapCard}>
            <Map marks={marks} center={defaultCenter} zoom={10} />
          </div>
          <div className={styles.graphCard}>
            <Graph data={predictionData} />
          </div>
        </div>
      </section>

      {/* SEÇÃO 3: TABELA HISTÓRICA DE ACIDENTES */}
      <section className={styles.section}>
        <DataCollection
          headers={["LOCALIZAÇÃO", "STATUS", "GRAVIDADE", "LINK"]}
          reports={reports}
          title="REGISTROS HISTÓRICOS DE ACIDENTES"
          buttonText={<span>VER MAIS DADOS HISTÓRICOS</span>}
        />
      </section>
    </div>
  );
}
