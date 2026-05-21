import styles from "./Map.module.css";
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

export default function Map(){
    const position = [-15.7801, -47.9292];

    return(
    <div className={styles.grafico}>
        <div className={styles.mapWrapper}>
            <MapContainer center={position} zoom={4} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; OpenStreetMap contributors'
                />
            </MapContainer>
        </div>
    </div>
    )
}