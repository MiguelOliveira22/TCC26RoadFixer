import { useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import styles from './Graph.module.css';
import FilledButton from './Button/FilledButton';

// Tooltip customizado com o estilo do site
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className={styles.customTooltip}>
        <p className={styles.tooltipLabel}>{`Km: ${label}`}</p>
        <p className={styles.tooltipValue}>
          Nível de Risco: <span>{payload[0].value.toFixed(2)}</span>
        </p>
      </div>
    );
  }
  return null;
};

export default function Graph({ data }) {
  const [kilometer, setKilometer] = useState(0);
  const [inputValue, setInputValue] = useState('0');

  let min = 0;
  let max = 25;

  if (kilometer < 25) {
    min = 0;
    max = kilometer + 25;
  } else if (kilometer > 427) {
    min = kilometer - 25;
    max = 453;
  } else {
    min = kilometer - 25;
    max = kilometer + 25;
  }

  const filterData = data ? data.slice(min, max) : [];
  const keyNames = filterData.length > 0 ? Object.keys(filterData[0]) : ['km', 'risco'];

  const updateData = () => {
    let numVal = Number(inputValue);

    if (isNaN(numVal) || numVal < 0) numVal = 0;
    if (numVal > 453) numVal = 453;

    setKilometer(numVal);
    setInputValue(String(numVal));
  };

  const updateInputValue = (e) => {
    const rawValue = e.target.value;

    if (rawValue === '') {
      setInputValue('');
      return;
    }

    const value = Number(rawValue);

    if (value > 453) {
      setInputValue('453');
    } else {
      setInputValue(rawValue);
    }
  };

  return (
    <div className={styles.graphCard}>
      {/* Cabeçalho decorativo do card */}
      <div className={styles.cardHeader}>
        <div>
          <h3 className={styles.cardTitle}>Análise de Risco da Via</h3>
          <p className={styles.cardSubtitle}>Visualização detalhada por trecho quilométrico</p>
        </div>
        <div className={styles.badgeKm}>
          Exibindo: <span>{min} km - {max} km</span>
        </div>
      </div>

      {/* Área do Gráfico */}
      <div className={styles.graphContainer}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={filterData} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
            <defs>
              {/* Gradiente de preenchimento para a linha de risco */}
              <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--laranja, #ff7300)" stopOpacity={0.4} />
                <stop offset="95%" stopColor="var(--laranja, #ff7300)" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.07)" vertical={false} />

            <XAxis
              dataKey={keyNames[0]}
              stroke="#888"
              tick={{ fill: '#aaa', fontSize: 11 }}
              dy={10}
              label={{
                value: 'Quilometragem (Km)',
                position: 'insideBottom',
                offset: -12,
                fill: '#888',
                fontSize: 12
              }}
            />

            <YAxis
              domain={[0, 10]}
              stroke="#888"
              tick={{ fill: '#aaa', fontSize: 11 }}
              label={{
                value: 'Nível de Risco',
                angle: -90,
                position: 'insideLeft',
                offset: 15,
                fill: '#888',
                fontSize: 12
              }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Area
              type="monotone"
              dataKey={keyNames[1]}
              stroke="var(--laranja, #ff7300)"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorRisk)"
              dot={{ r: 3, fill: 'var(--laranja, #ff7300)', strokeWidth: 1 }}
              activeDot={{ r: 6, fill: '#fff', stroke: 'var(--laranja, #ff7300)', strokeWidth: 2 }}
              isAnimationActive={true}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Filtro estilizado */}
      <div className={styles.filterBar}>
        <div className={styles.filterGroup}>
          <label className={styles.label}>
            Filtrar Trecho <span className={styles.labelHint}>(0 a 453 km)</span>
          </label>
          
          <div className={styles.inputWrapper}>
            <input
              type="number"
              max="453"
              min="0"
              value={inputValue}
              className={styles.input}
              onChange={updateInputValue}
              placeholder="Ex: 120"
            />
            <span className={styles.inputUnit}>km</span>
          </div>
        </div>

        <div className={styles.btnFilter}>
          <FilledButton value={"Filtrar Vista"} action={updateData} />
        </div>
      </div>
    </div>
  );
}