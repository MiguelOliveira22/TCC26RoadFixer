import styles from "./EstatisticasPage.module.css";

import 'leaflet/dist/leaflet.css';
import DataCollection from "../components/DataCollection";
import Graph from "../components/Graph";
import Map from "../components/Map"


function MockedData()
{
    
    let data = [];
    for(let i = 0; i < 453; i++){
        const randomInt = Math.random() * 10
        data.push({"KM": String(i+1), "risk": randomInt})
    }
    return data
}

export default function EstatisticasPage() {
    const reports = [
        { id: 1, data: ["BR-330 KM 200" , "4 PESSOAS" , "ALTA" , {url: ""}]},
        { id: 2, data: ["BR-330 KM 012" , "1 PESSOA"  , "BAIXA" , {url: ""}]},
        { id: 3, data: ["BR-330 KM 167" , "3 PESSOAS" , "MEDIA" , {url: ""}]},
    ];


    return (
        <>
            <section className={styles.section}>
                <div className={styles.header}>
                    <p className={styles.kicker}>MAPA DE RISCO REAL</p>
                    <h2 className={styles.title}>MAPA <span style={{ color: 'var(--laranja)' }}>INTERATIVO</span></h2>
                    <p className={styles.subtitle}>Tela dedicada para consultar os relatos e visualizar os pontos de atenção no mapa.</p>
                </div>
                
                <Map/>
                <Graph
                    data={MockedData()}
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
                    data={MockedData()}
                />
            </section>

            <DataCollection headers={["LOCALIZAÇÃO", "STATUS", "GRAVIDADE", "LINK"]} reports={reports} idCabecalho={1}></DataCollection>

        </>
    );
}