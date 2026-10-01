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
  if (!res.ok) throw new Error(`Falha ao carregar risco: HTTP ${res.status}`);
  const data = await res.json();
  const formatted = (Array.isArray(data.risk) ? data.risk : []).map((valor, index) => ({ KM: String(index), risco: valor }));
  return { formatted, metadata: data, details: Array.isArray(data.trechos) ? data.trechos : [] };
}

export default function EstatisticasPage() {
  const [reports, setReports] = useState(null);
  const [riskData, setRiskData] = useState([]);
  const [riskMetadata, setRiskMetadata] = useState(null);
  const [riskDetails, setRiskDetails] = useState([]);

  // Ponto central padrão para manter a alinhamento do mapa
  const defaultCenter = [-22.92506, -47.08692];
  const marks = [{ position: defaultCenter, information: "Rodovia Anhanguera (SP-330)" }];

  useEffect(() => {
    const loadData = async () => {
      try {
        const [reportsData, risk] = await Promise.all([getReports(), getRiskData()]);
        setReports(reportsData);
        setRiskData(risk.formatted);
        setRiskMetadata(risk.metadata);
        setRiskDetails(risk.details);
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
      {riskMetadata && (
        <section className={styles.metadataCard} aria-label="Atualização e qualidade da previsão">
          <div>
            <strong>Previsão para {riskMetadata.periodo_previsto || "período não informado"}</strong>
            <span>
              Atualizada em {riskMetadata.last_update
                ? new Date(riskMetadata.last_update).toLocaleString("pt-BR")
                : "data não informada"}
            </span>
          </div>
          <p>{riskMetadata.aviso || riskMetadata.metodo}</p>
          {typeof riskMetadata.qualidade_dados?.cobertura_fluxo_recente === "number" ? (
            <p>
              Fluxo recente disponível em {Math.round(riskMetadata.qualidade_dados.cobertura_fluxo_recente * 100)}%
              {" "}dos trechos previstos. Os dois sentidos estão agregados em células de 1 km.
            </p>
          ) : riskMetadata.qualidade_dados?.exposicao_veiculo_km && (
            <p>{riskMetadata.qualidade_dados.exposicao_veiculo_km}</p>
          )}
          {riskMetadata.faixa_previsao?.aviso && <small>{riskMetadata.faixa_previsao.aviso}</small>}
          {riskMetadata.metricas?.baselines && (
            <div className={styles.baselineSummary}>
              <strong>Comparação no teste temporal</strong>
              <span>Captura média mensal da taxa observada nos 10% de trechos priorizados.</span>
              <span>ExtraTrees: {((riskMetadata.metricas.captura_mensal_teste || 0) * 100).toFixed(1)}%</span>
              <span>Taxa dos últimos 365 dias: {((riskMetadata.metricas.baselines.taxa_historica_365d?.teste_ano_final || 0) * 100).toFixed(1)}%</span>
              <span>Média histórica: {((riskMetadata.metricas.baselines.taxa_media_historica?.teste_ano_final || 0) * 100).toFixed(1)}%</span>
            </div>
          )}
        </section>
      )}

      {/* SEÇÃO 1: ÍNDICE DE PRIORIZAÇÃO */}
      <section className={styles.section}>
        <div className={styles.header}>
          <p className={styles.kicker}>PREVISÃO PARA TRIAGEM HUMANA</p>
          <h2 className={styles.title}>
            ÍNDICE DE <span className={styles.highlight}>PRIORIZAÇÃO</span>
          </h2>
          <p className={styles.subtitle}>
            Escala relativa de 0 a 10 baseada na taxa prevista de severidade por milhão de veículos-km. Não representa probabilidade de acidente.
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

      {/* SEÇÃO 2: EVIDÊNCIAS E INCERTEZA */}
      <section className={styles.section}>
        <div className={styles.header}>
          <p className={styles.kicker}>SINAIS OBSERVADOS, NÃO CAUSAS COMPROVADAS</p>
          <h2 className={styles.title}>
            EVIDÊNCIAS POR <span className={styles.highlight}>TRECHO</span>
          </h2>
          <p className={styles.subtitle}>
            Faixas de referência calculadas com os erros do ano de teste. A quantidade de histórico e a atualidade do tráfego ajudam a interpretar cada prioridade.
          </p>
        </div>

        <div className={styles.evidenceTableWrap}>
          <table className={styles.evidenceTable}>
            <thead>
              <tr>
                <th>KM</th><th>Índice</th><th>Taxa prevista</th><th>Faixa de referência</th><th>Suporte dos dados</th><th>Evidências</th>
              </tr>
            </thead>
            <tbody>
              {riskDetails.slice(0, 10).map((segment) => (
                <tr key={segment.km}>
                  <td>{segment.km}</td>
                  <td>{Number(segment.indice_risco).toFixed(2)}</td>
                  <td>{Number(segment.taxa_prevista).toFixed(3)}</td>
                  <td>{Number(segment.limite_inferior).toFixed(3)} – {Number(segment.limite_superior).toFixed(3)}</td>
                  <td>{segment.confiabilidade_dados}</td>
                  <td>{(segment.evidencias || []).join("; ")}</td>
                </tr>
              ))}
              {riskDetails.length === 0 && (
                <tr><td colSpan="6">A API ainda não publicou evidências detalhadas por trecho.</td></tr>
              )}
            </tbody>
          </table>
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
