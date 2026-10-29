import styles from "./EstatisticasPage.module.css";
import 'leaflet/dist/leaflet.css';
import DataCollection from "../components/DataCollection";
import Graph from "../components/Graph";
import Map from "../components/Map";
import { useEffect, useState } from "react";
import { apiPath } from "../Constants";

async function getReports() {
  const res = await fetch(apiPath + "accidentHistory");
  if (!res.ok) throw new Error(`accidentHistory: HTTP ${res.status}`);
  const data = await res.json();
  return (data.content ?? []).map((valor) => ({ id: valor.id, data: valor.data }));
}

async function getRiskData() {
  const res = await fetch(apiPath + "riskData");
  if (!res.ok) throw new Error(`riskData: HTTP ${res.status}`);
  const data = await res.json();
  return (Array.isArray(data.risk) ? data.risk : []).map((valor, index) => ({
    KM: String(index),
    risco: valor,
  }));
}

async function getPredictionData() {
  const res = await fetch(apiPath + "predictionData");
  if (!res.ok) throw new Error(`predictionData: HTTP ${res.status}`);
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
  const [reports, setReports] = useState([]);
  const [riskData, setRiskData] = useState([]);
  const [predictionData, setPredictionData] = useState([]);
  const [predictionPeriod, setPredictionPeriod] = useState(null);

  // Ponto central padrão para manter o alinhamento do mapa
  const defaultCenter = [-22.92506, -47.08692];
  const marks = [{ position: defaultCenter, information: "Rodovia Anhanguera (SP-330)" }];

  useEffect(() => {
    // allSettled: se uma requisição falhar, as outras seções ainda carregam
    Promise.allSettled([getReports(), getRiskData(), getPredictionData()]).then(
      ([reportsRes, riskRes, predRes]) => {
        if (reportsRes.status === "fulfilled") setReports(reportsRes.value);
        else console.error("Erro em accidentHistory:", reportsRes.reason);

        if (riskRes.status === "fulfilled") setRiskData(riskRes.value);
        else console.error("Erro em riskData:", riskRes.reason);

        if (predRes.status === "fulfilled") {
          setPredictionData(predRes.value.values);
          setPredictionPeriod(predRes.value.period);
        } else console.error("Erro em predictionData:", predRes.reason);
      }
    );
  }, []);

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

        <div className={styles.dataGrid}>
          <div className={styles.mapCard}>
            <Map risk={riskData} marks={marks} center={defaultCenter} zoom={10} />
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
            <Map risk={predictionData} marks={marks} center={defaultCenter} zoom={10} />
          </div>
          <div className={styles.graphCard}>
            <Graph data={predictionData} />
          </div>
        </div>
      </section>

      {/* SEÇÃO 3: TABELA HISTÓRICA DE ACIDENTES */}
      <section className={styles.section}>
        <DataCollection
          headers={["DATA", "TRECHO QUILOMÉTRICO", "LINK"]}
          reports={reports}
          title="REGISTROS HISTÓRICOS DE ACIDENTES"
          buttonText={<span>VER MAIS DADOS HISTÓRICOS</span>}
        />
      </section>
    </div>
  );
} 