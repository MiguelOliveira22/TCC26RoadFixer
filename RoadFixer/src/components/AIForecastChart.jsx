import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import styles from "./AIForecastChart.module.css";

const integerFormatter = new Intl.NumberFormat("pt-BR", {
  maximumFractionDigits: 0,
});

function formatDate(value) {
  return new Date(`${value}T12:00:00`).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
  });
}

function tooltipValue(value, name) {
  if (Array.isArray(value)) {
    return [`${integerFormatter.format(value[0])} a ${integerFormatter.format(value[1])}`, name];
  }
  return [integerFormatter.format(value), name];
}

export default function AIForecastChart({ data, history }) {
  const historicalData = history.map((item) => ({
    data: item.data,
    trafegoObservado: item.volume_trafego.observado,
    acidentesObservados: item.acidentes.observado,
  }));
  const forecastData = data.map((item) => ({
    data: item.data,
    trafegoPrevisto: item.volume_trafego.previsao,
    trafegoFaixa: [
      item.volume_trafego.limite_inferior_95,
      item.volume_trafego.limite_superior_95,
    ],
    acidentesPrevistos: item.acidentes.previsao,
    acidentesFaixa: [
      item.acidentes.limite_inferior_95,
      item.acidentes.limite_superior_95,
    ],
  }));
  const chartData = [...historicalData, ...forecastData];
  const forecastStart = forecastData[0]?.data;
  const tooltipStyle = {
    background: "rgba(18, 18, 18, 0.97)",
    border: "1px solid rgba(255, 115, 0, 0.45)",
    borderRadius: "8px",
    color: "#fff",
  };

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div>
          <h3>Histórico e previsão diária</h3>
          <p>Os gráficos separam as escalas para facilitar a comparação.</p>
        </div>
        <div className={styles.legend} aria-label="Legenda dos gráficos">
          <span><i className={styles.observedLine}></i>Observado</span>
          <span><i className={styles.forecastLine}></i>Previsto</span>
          <span><i className={styles.rangeBox}></i>Faixa provável</span>
        </div>
      </div>

      <div className={styles.chartGrid}>
        <section className={styles.chartPanel} aria-label="Gráfico de tráfego diário">
          <div className={styles.panelHeader}>
            <strong>Volume de tráfego</strong>
            <span>veículos por dia</span>
          </div>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} syncId="previsao-diaria" margin={{ top: 10, right: 10, left: 8, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.07)" vertical={false} />
                <XAxis dataKey="data" tickFormatter={formatDate} tick={{ fill: "#999", fontSize: 11 }} stroke="#555" minTickGap={24} />
                <YAxis tickFormatter={(value) => `${(value / 1000000).toFixed(1)} mi`} tick={{ fill: "#999", fontSize: 11 }} stroke="#555" width={52} />
                <Tooltip labelFormatter={(value) => formatDate(value)} formatter={tooltipValue} contentStyle={tooltipStyle} />
                {forecastStart && <ReferenceLine x={forecastStart} stroke="#777" strokeDasharray="3 3" />}
                <Area type="monotone" dataKey="trafegoFaixa" name="Faixa provável" stroke="none" fill="#ff7300" fillOpacity={0.14} />
                <Line type="monotone" dataKey="trafegoObservado" name="Observado" stroke="#d8d8d8" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="trafegoPrevisto" name="Previsto" stroke="#ff7300" strokeWidth={2.5} strokeDasharray="7 4" dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className={styles.chartPanel} aria-label="Gráfico de acidentes diários">
          <div className={styles.panelHeader}>
            <strong>Número de acidentes</strong>
            <span>ocorrências por dia</span>
          </div>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} syncId="previsao-diaria" margin={{ top: 10, right: 10, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.07)" vertical={false} />
                <XAxis dataKey="data" tickFormatter={formatDate} tick={{ fill: "#999", fontSize: 11 }} stroke="#555" minTickGap={24} />
                <YAxis allowDecimals={false} tick={{ fill: "#999", fontSize: 11 }} stroke="#555" width={34} />
                <Tooltip labelFormatter={(value) => formatDate(value)} formatter={tooltipValue} contentStyle={tooltipStyle} />
                {forecastStart && <ReferenceLine x={forecastStart} stroke="#777" strokeDasharray="3 3" />}
                <Area type="monotone" dataKey="acidentesFaixa" name="Faixa provável" stroke="none" fill="#2aa8f2" fillOpacity={0.15} />
                <Line type="monotone" dataKey="acidentesObservados" name="Observado" stroke="#d8d8d8" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="acidentesPrevistos" name="Previsto" stroke="#2aa8f2" strokeWidth={2.5} strokeDasharray="7 4" dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </div>
  );
}
