import styles from "./EstatisticasPage.module.css";
import 'leaflet/dist/leaflet.css';
import DataCollection from "../components/DataCollection";
import Graph from "../components/Graph";
import Map from "../components/Map";
import { useEffect, useState } from "react";
import { apiPath } from "../Constants";

async function getReports() {
  const res = await fetch(apiPath + "accidentHistory/");
  const data = await res.json();
  const formatted = data.content.map((valor) => ({ id: valor.id, data: valor.data }));
  return formatted;
}

async function getRiskData() {
  const res = await fetch(apiPath + "riskData/");
  const data = await res.json();
  console.log(data)
  const formatted = data['risk'].map((valor, index) => ({ KM: String(index + 1), risco: valor }));
  return formatted;
}

export default function EstatisticasPage() {
  const [reports, setReports] = useState(null);
  const [riskData, setRiskData] = useState([]);

  // Ponto central padrão para manter a alinhamento do mapa
  const defaultCenter = [-22.92506, -47.08692];
  const marks = [{ position: defaultCenter, information: "Rodovia Anhanguera (SP-330)" }];

  useEffect(() => {
    const loadData = async () => {
      try {
        const [reportsData, risk] = await Promise.all([getReports(), getRiskData()]);
        setReports(reportsData);
        setRiskData(risk);
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
      {/* SEÇÃO 1: RISCO REAL */}
      <section className={styles.section}>
        <div className={styles.header}>
          <p className={styles.kicker}>DIAGNÓSTICO INICIAL</p>
          <h2 className={styles.title}>
            MAPA DE RISCO <span className={styles.highlight}>REAL</span>
          </h2>
          <p className={styles.subtitle}>
            Visualização dos índices de risco registrados em tempo real ao longo dos trechos da via.
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

      {/* SEÇÃO 2: RISCO CORRIGIDO */}
      <section className={styles.section}>
        <div className={styles.header}>
          <p className={styles.kicker}>PROJEÇÃO E OTIMIZAÇÃO</p>
          <h2 className={styles.title}>
            MAPA DE RISCO <span className={styles.highlight}>CORRIGIDO</span>
          </h2>
          <p className={styles.subtitle}>
            Estimativa de mitigação dos pontos críticos após a aplicação das intervenções recomendadas.
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