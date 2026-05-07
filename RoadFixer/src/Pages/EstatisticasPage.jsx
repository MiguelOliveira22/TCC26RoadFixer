import styles from "./EstatisticasPage.module.css";
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function EstatisticasPage() {
    const position = [-15.7801, -47.9292];

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

            <section className={styles.section}>
                <div className={styles.header}>
                <p className={styles.kicker}>VISÃO OPERACIONAL</p>
                <h2 className={styles.title}>MAPA <span style={{ color: 'var(--laranja)' }}>INTERATIVO</span></h2>
                <p className={styles.subtitle}>Tela dedicada para consultar os relatos e visualizar os pontos de atenção no mapa.</p>
                </div>
                <div className={styles.mapWrapper}>
                <MapContainer center={position} zoom={4} style={{ height: '100%', width: '100%' }}>
                    <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; OpenStreetMap contributors'
                    />
                </MapContainer>
                </div>
            </section>
        </>
    );
}