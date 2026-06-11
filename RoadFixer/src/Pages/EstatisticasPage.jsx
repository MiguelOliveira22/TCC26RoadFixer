import styles from "./EstatisticasPage.module.css";

import 'leaflet/dist/leaflet.css';
import DataCollection from "../components/DataCollection";
import Graph from "../components/Graph";
import Map from "../components/Map"
import { useEffect, useState } from "react";
import { apiPath } from "../Constants";

async function getReports(){
    const res = await fetch(apiPath+"accidentHistory/");
    const data = await res.json();
    const formatted = data.content.map((valor) => ({ id: valor.id, data: valor.data }));
    return formatted
}

async function GetRiskData()
{
    const res = await fetch(apiPath+"riskData/");
    const data = await res.json();
    const formatted = data.map((valor, index) => ({ KM: String(index + 1), risco: valor }));
    return formatted
}

export default function EstatisticasPage() {
      const [reports, setReports] = useState(null)
    
      useEffect(() => {
              const loadData = async () => {
                  try {
                      const data = await getReports();
                      setReports(data);
                  } catch (error) {
                   console.error(error);
                  }
              };
      
              loadData()
          }, []);

    const marks = [{position: [-22.92506, -47.08692], information: "Rodovia Anhanguera (SP-330)"}];

    const [ response, setResponse ] = useState()

    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await GetRiskData();
                setResponse(data);
            } catch (error) {
             console.error(error);
            }
        };

        loadData()
    }, []);

    if (reports === null) {
        return (
          <div className={styles.loadingContainer}>
            <p>Carregando informações...</p>
          </div>
        );
      }

    return (
        <>
            <section className={styles.section}>
                <div className={styles.header}>
                    <p className={styles.kicker}>MAPA DE RISCO REAL</p>
                    <h2 className={styles.title}>MAPA <span style={{ color: 'var(--laranja)' }}>INTERATIVO</span></h2>
                    <p className={styles.subtitle}>Tela dedicada para consultar os relatos e visualizar os pontos de atenção no mapa.</p>
                </div>
                
                <Map
                marks={marks}
                />
                <Graph
                    data={response}
                />
            </section>

            <section className={styles.section}>
                <div className={styles.header}>
                <p className={styles.kicker}>MAPA DE RISCO CORRIGIDO</p>
                <h2 className={styles.title}>MAPA <span style={{ color: 'var(--laranja)' }}>INTERATIVO</span></h2>
                <p className={styles.subtitle}>Tela dedicada para consultar os relatos e visualizar os pontos de atenção no mapa.</p>
                </div>
                <Map/>
                <Graph
                    data={response}
                />
            </section>

            <DataCollection headers={["LOCALIZAÇÃO", "STATUS", "GRAVIDADE", "LINK"]} reports={reports} title="DADOS HISTÓRICOS" buttonText={(<span>VER MAIS DADOS HISTÓRICOS</span>)}></DataCollection>

        </>
    );
}