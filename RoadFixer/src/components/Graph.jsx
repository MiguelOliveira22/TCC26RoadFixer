import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Graph({data, max = 50, min = 0}){
    let filterData = []
    for(let i = min; i < max; i++){
        filterData.push(data[i])
    }
    const keyNames = Object.keys(filterData[0])
    return(
        <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
            <LineChart data={filterData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={keyNames[0]}/>
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey={keyNames[1]} stroke="#8884d8" />
            </LineChart>
            </ResponsiveContainer>
        </div>
    )
}

Graph.prop