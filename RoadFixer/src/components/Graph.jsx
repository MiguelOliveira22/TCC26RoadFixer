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

  return (
    <div>
      <p>Quilometragem:</p>

      <input
        type="number"
        max="453"
        min="0"
        value={inputValue}
        onChange={(e) => setInputValue(Number(e.target.value))}
      />

      <button onClick={updateData}>
        Filtrar
      </button>

      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={filterData}>
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey={keyNames[0]} />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey={keyNames[1]}
              stroke="#8884d8"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}