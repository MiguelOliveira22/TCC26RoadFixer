import styles from "./EstatisticasPage.module.css";
import 'leaflet/dist/leaflet.css';
import DataCollection from "../components/DataCollection";
import Graph from "../components/Graph";
import Map from "../components/Map";
import AIForecastChart from "../components/AIForecastChart";
import { useEffect, useState } from "react";
import { apiPath } from "../Constants";

const integerFormatter = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });

function formatDate(value) {
  return new Date(`${value}T12:00:00`).toLocaleDateString("pt-BR");
}

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

async function getAIForecast(days, historyDays, signal) {
  const params = new URLSearchParams({
    days: String(days),
    history_days: String(historyDays),
  });
  const res = await fetch(`${apiPath}ai/forecast?${params}`, { signal });
  if (!res.ok) {
    const response = await res.json().catch(() => ({}));
    throw new Error(response.detail || `Falha ao carregar previsão: HTTP ${res.status}`);
  }
  return res.json();
}

export default function EstatisticasPage() {
  const [reports, setReports] = useState(null);
  const [riskData, setRiskData] = useState([]);
  const [riskMetadata, setRiskMetadata] = useState(null);
  const [riskDetails, setRiskDetails] = useState([]);
  const [aiForecast, setAiForecast] = useState(null);
  const [aiForecastError, setAiForecastError] = useState("");
  const [analysisDays, setAnalysisDays] = useState(30);
  const [forecastLoading, setForecastLoading] = useState(true);

  // Ponto central padrão para manter a alinhamento do mapa
  const defaultCenter = [-22.92506, -47.08692];
  const marks = [{ position: defaultCenter, information: "Rodovia Anhanguera (SP-330)" }];

  useEffect(() => {
    const loadData = async () => {
      const [reportsResult, riskResult] = await Promise.allSettled([
        getReports(),
        getRiskData(),
      ]);

      if (reportsResult.status === "fulfilled") {
        setReports(reportsResult.value);
      } else {
        console.error("Erro ao carregar histórico:", reportsResult.reason);
        setReports([]);
      }

      if (riskResult.status === "fulfilled") {
        setRiskData(riskResult.value.formatted);
        setRiskMetadata(riskResult.value.metadata);
        setRiskDetails(riskResult.value.details);
      } else {
        console.error("Erro ao carregar risco:", riskResult.reason);
      }

    };

    loadData();
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    const loadForecast = async () => {
      setForecastLoading(true);
      setAiForecastError("");
      try {
        const result = await getAIForecast(analysisDays, analysisDays, controller.signal);
        setAiForecast(result);
      } catch (error) {
        if (error.name !== "AbortError") {
          console.error("Erro ao carregar previsão da IA:", error);
          setAiForecastError(error.message || "A previsão está indisponível.");
        }
      } finally {
        if (!controller.signal.aborted) setForecastLoading(false);
      }
    };

    loadForecast();
    return () => controller.abort();
  }, [analysisDays]);

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
      <section className={styles.section} aria-labelledby="ai-forecast-title">
        <div className={styles.header}>
          <p className={styles.kicker}>PREVISÃO COM INTELIGÊNCIA ARTIFICIAL</p>
          <h2 className={styles.title} id="ai-forecast-title">
            PREVISÃO DE <span className={styles.highlight}>TRÁFEGO E ACIDENTES</span>
          </h2>
          <p className={styles.subtitle}>
            O sistema estima primeiro o volume de tráfego. Esse resultado é usado para calcular a previsão diária de acidentes.
          </p>
        </div>

        <div className={styles.forecastControls} aria-label="Períodos do gráfico">
          <label>
            Período de análise
            <select value={analysisDays} onChange={(event) => setAnalysisDays(Number(event.target.value))}>
              <option value={7}>7 dias</option>
              <option value={15}>15 dias</option>
              <option value={30}>30 dias</option>
            </select>
          </label>
          {forecastLoading && <span className={styles.forecastUpdating}>Atualizando dados...</span>}
        </div>

        {aiForecast ? (
          <>
            <div className={styles.forecastSummaryGrid}>
              <article className={styles.forecastKpi}>
                <span>Tráfego previsto por dia</span>
                <strong>{integerFormatter.format(aiForecast.resumo.volume_medio_diario)}</strong>
                <small>média do período selecionado</small>
              </article>
              <article className={styles.forecastKpi}>
                <span>Acidentes previstos</span>
                <strong>{integerFormatter.format(aiForecast.resumo.acidentes_previstos_total)}</strong>
                <small>total no período selecionado</small>
              </article>
              <article className={styles.forecastKpi}>
                <span>Previsão apresentada</span>
                <strong>{aiForecast.periodo.dias} dias</strong>
                <small>{formatDate(aiForecast.periodo.inicio)} a {formatDate(aiForecast.periodo.fim)}</small>
              </article>
            </div>

            <AIForecastChart data={aiForecast.previsoes} history={aiForecast.historico} />

            <div className={styles.forecastExplanation}>
              <strong>Como interpretar</strong>
              <span>
                A linha contínua mostra os dados já registrados. A linha tracejada mostra a previsão, e a área colorida representa a variação possível do resultado.
              </span>
            </div>
          </>
        ) : (
          <div className={styles.forecastError} role="status">
            <strong>Previsão da IA temporariamente indisponível</strong>
            <span>{aiForecastError || "Carregando os modelos de previsão..."}</span>
          </div>
        )}
      </section>

      {riskMetadata && (
        <section className={styles.metadataCard} aria-label="Atualização e qualidade da previsão">
          <div>
            <strong>Mapa de priorização por trecho</strong>
            <span>
              Atualizada em {riskMetadata.last_update
                ? new Date(riskMetadata.last_update).toLocaleString("pt-BR")
                : "data não informada"}
            </span>
          </div>
          <p>O índice destaca os trechos que merecem atenção e apoia a análise preventiva da rodovia.</p>
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
            <Map risk={riskData} marks={marks} center={defaultCenter} zoom={10} />
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
