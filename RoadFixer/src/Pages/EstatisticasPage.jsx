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

const TIPOS_DADO = [
  { label: "Risco", rota: apiPath + "riskData", escalaFixa: true }, // vem de /riskData, já em 0–10
  { label: "Volume de tráfego", rota: null, extrair: (d) => d.valores },
  { label: "Numero de mortes", rota: null, extrair: (d) => d.valores },
  { label: "Números de acidentados agregados", rota: null, extrair: (d) => d.valores },
  { label: "Volume médio de acidentes agregados", rota: null, extrair: (d) => d.valores },
];
const TIPO_PADRAO = "Risco";

async function getSerie(tipo) {
  const res = await fetch(apiPath + tipo.rota);
  if (!res.ok) throw new Error(`Falha ao carregar ${tipo.label}: HTTP ${res.status}`);
  const data = await res.json();
  return (tipo.extrair(data) || []).map((v) => Number(v) || 0);
}

export default function EstatisticasPage() {
  const [reports, setReports] = useState(null);
  const [series, setSeries] = useState({});            // { "Risco": [..], "Volume de tráfego": [..] }
  const [tipoDado, setTipoDado] = useState(TIPO_PADRAO);
  const [inputValue, setInputValue] = useState(TIPO_PADRAO);
  const [riskMetadata, setRiskMetadata] = useState(null);
  const [riskDetails, setRiskDetails] = useState([]);

  // Ponto central padrão para manter a alinhamento do mapa
  const defaultCenter = [-22.92506, -47.08692];
  const marks = [{ position: defaultCenter, information: "Rodovia Anhanguera (SP-330)" }];

  useEffect(() => {
    const loadData = async () => {
      try {
        const extras = TIPOS_DADO.filter((t) => t.rota);
        const [reportsData, risk, resultados] = await Promise.all([
          getReports(),
          getRiskData(),
          Promise.allSettled(extras.map(getSerie)), // uma rota com erro não derruba as outras
        ]);

        const novas = { Risco: risk.formatted.map((r) => r.risco) };
        resultados.forEach((r, i) => {
          if (r.status === "fulfilled") novas[extras[i].label] = r.value;
          else console.error(r.reason);
        });

        setReports(reportsData);
        setSeries(novas);
        setRiskMetadata(risk.metadata);
        setRiskDetails(risk.details);
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
