import styles from "./EstatisticasPage.module.css";
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import DataCollection from "../components/DataCollection";

export default function EstatisticasPage() {
    const position = [-15.7801, -47.9292];
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
                <div className={styles.grafico}>
                    <div className={styles.mapWrapper}>
                        <MapContainer center={position} zoom={4} style={{ height: '100%', width: '100%' }}>
                            <TileLayer
                            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                            attribution='&copy; OpenStreetMap contributors'
                            />
                        </MapContainer>
                    </div>
                    <div className={styles.graficoLinhas}>
                        Gráfico
                    </div>
                </div>
            </section>

            <DataCollection headers={["LOCALIZAÇÃO", "STATUS", "GRAVIDADE", "LINK"]} reports={reports} idCabecalho={1}></DataCollection>

            <section className={styles.section}>
                <div className={styles.header}>
                <p className={styles.kicker}>MAPA DE RISCO CORRIGIDO</p>
                <h2 className={styles.title}>MAPA <span style={{ color: 'var(--laranja)' }}>INTERATIVO</span></h2>
                <p className={styles.subtitle}>Tela dedicada para consultar os relatos e visualizar os pontos de atenção no mapa.</p>
                </div>
                <div className={styles.grafico}>
                    <div className={styles.mapWrapper}>
                        <MapContainer center={position} zoom={4} style={{ height: '100%', width: '100%' }}>
                            <TileLayer
                            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                            attribution='&copy; OpenStreetMap contributors'
                            />
                        </MapContainer>
                    </div>
                    <div className={styles.graficoLinhas}>
                        Gráfico
                    </div>
                </div>
            </section>
        </>
    );
}