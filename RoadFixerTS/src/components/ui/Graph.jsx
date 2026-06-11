import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import styles from './Graph.module.css'
import FilledButton from './Button/FilledButton'

export default function Graph({ data }) {
  const [kilometer, setKilometer] = useState(0);
  const [inputValue, setInputValue] = useState(0);

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

  const keyNames =
    filterData.length > 0 ? Object.keys(filterData[0]) : [];

  const updateData = () => {
        setKilometer(inputValue);
  };

  const updateInputValue = (e) =>{
    e.target.value = Number(e.target.value)
    const value = e.target.value

    if(value > 453){
        setInputValue(453)
    }
    else if(value <= 0){
        setInputValue(0)
    }
    else{
        setInputValue(Number(value))
    }
  }

  return (
    <div className={styles.divGraph}>
        <div className={styles.graph}>
            <ResponsiveContainer>
                <LineChart data={filterData} margin={{ top: 0, right: 0, left: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3"/>

                    <XAxis dataKey={keyNames[0]} tick={{ fontSize: 12 }} label={{ value: 'Quilometragem', position: 'middle', offset: -10 , dy: 15}} />

                    <YAxis domain={[0, 10]} label={{ value: 'Risco', position: 'middle', offset: 0, dx: -15}} />

                    <Tooltip />

                    <Line
                    type="linear"
                    dataKey={keyNames[1]}
                    stroke="#8884d8"
                    connectNulls
                    isAnimationActive={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
        <div className={styles.filterDiv}>
            <div className={styles.filterInput}>
                <p className={styles.text}>Quilometragem (± 25):</p>

                <input
                type="number"
                max="453"
                min="0"
                value={inputValue}
                className={styles.input}
                onChange={updateInputValue}
                />
            </div>
            <div className={styles.btnFilter}>
                <FilledButton
                value={"Filtrar"}
                action={updateData}
                />
            </div>
        </div>
    </div>
  );
}