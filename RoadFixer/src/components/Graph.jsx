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

  const filterData = data.slice(min, max);

  const keyNames =
    filterData.length > 0 ? Object.keys(filterData[0]) : [];

  const updateData = () => {
        setKilometer(Number(inputValue));
  };

  const updateInputValue = (e) =>{
    const value = e.target.value

    if(value > 453){
        setInputValue(453)
    }
    else if(value < 0){
        setInputValue(0)
    }
    else{
        setInputValue(Number(value))
    }
  }

  return (
    <div style={{margin: 10}}>
        <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
                <LineChart data={filterData}>
                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey={keyNames[0]} tick={{ fontSize: 12}} />

                    <YAxis domain={[0, 10]}/>

                    <Tooltip />

                    <Line
                    type="monotone"
                    dataKey={keyNames[1]}
                    stroke="#8884d8"
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