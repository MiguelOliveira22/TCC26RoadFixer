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
  const data = await res.json();
  const formatted = data.risk.map((valor, index) => ({ KM: String(index), risco: valor }));
  return formatted;
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

  if (reports === null) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
        <p className={styles.loadingText}>Carregando estatísticas...</p>
      </div>
    );
  }

  return (
    <div className={styles.pageWrapper}>
      {/* SEÇÃO 1: ÍNDICE HISTÓRICO */}
      <section className={styles.section}>
        <div className={styles.header}>
          <p className={styles.kicker}>DIAGNÓSTICO INICIAL</p>
          <h2 className={styles.title}>
            ÍNDICE DE RISCO <span className={styles.highlight}>HISTÓRICO</span>
          </h2>
          <p className={styles.subtitle}>
            Índice heurístico atualizado diariamente a partir dos acidentes históricos e das condições climáticas.
          </p>
        </div>

        <div className={styles.dataGrid}>
          <div className={styles.mapCard}>
            <Map marks={marks} center={defaultCenter} zoom={10} />
          </div>
          <div className={styles.graphCard}>
            <Graph data={riskData} />
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
