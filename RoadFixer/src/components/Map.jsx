import styles from "./Map.module.css";
import { CircleMarker, MapContainer, Popup, TileLayer, GeoJSON } from 'react-leaflet';
import anhangueraData from "../anhanguera.json";


const ANHANGUERA_POSITION = [-22.92506, -47.08692]

const SAO_PAULO_BOUNDS = [
    [-25.4, -53.2],
    [-19.7, -44.0],
];

const anhangueraStyle = {
        color: "var(--laranja)", // Usa a sua variável de cor ou um valor fixo como '#ff5500'
        weight: 4,               // Espessura da linha
        opacity: 0.8             // Opacidade da linha
    };

export default function Map({marks}){
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
                {anhangueraData && (
                        <GeoJSON 
                            data={anhangueraData} 
                            style={anhangueraStyle} 
                        />
                )}

                {
                    Array.isArray(marks) && marks.map((mark, index) => (
                        <CircleMarker
                            key={index}
                            center={mark.position}
                            radius={10}
                            pathOptions={{ color: 'var(--laranja)', fillColor: 'var(--laranja)', fillOpacity: 0.35 }}
                        >
                            <Popup>
                                {mark.information}
                            </Popup>
                        </CircleMarker>
                    ))
                }
            </MapContainer>
        </div>
    </div>
    )
}
