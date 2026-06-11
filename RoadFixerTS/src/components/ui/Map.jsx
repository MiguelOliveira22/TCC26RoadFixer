import styles from "./Map.module.css";
import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet';

const ANHANGUERA_POSITION = [-22.92506, -47.08692];
const SAO_PAULO_BOUNDS = [
    [-25.4, -53.2],
    [-19.7, -44.0],
];

export default function Map(){
    return(
    <div className={styles.grafico}>
        <div className={styles.mapWrapper}>
            <MapContainer
                center={ANHANGUERA_POSITION}
                zoom={11}
                minZoom={7}
                maxZoom={16}
                maxBounds={SAO_PAULO_BOUNDS}
                maxBoundsViscosity={1}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    noWrap
                    bounds={SAO_PAULO_BOUNDS}
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; OpenStreetMap contributors'
                />
                <CircleMarker
                    center={ANHANGUERA_POSITION}
                    radius={10}
                    pathOptions={{ color: 'var(--laranja)', fillColor: 'var(--laranja)', fillOpacity: 0.35 }}
                >
                    <Popup>Rodovia Anhanguera (SP-330)</Popup>
                </CircleMarker>
            </MapContainer>
        </div>
    </div>
    )
}
