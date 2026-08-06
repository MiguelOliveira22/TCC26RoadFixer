import { useEffect } from 'react';
import { CircleMarker, MapContainer, Popup, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import anhangueraData from "../anhanguera.json";
import styles from "./Map.module.css";

const ANHANGUERA_POSITION = [-22.92506, -47.08692];

const SAO_PAULO_BOUNDS = [
    [-25.4, -53.2],
    [-19.7, -44.0],
];

const ANHANGUERA_STYLE = {
    color: "var(--laranja)",
    weight: 4,
    opacity: 0.8
};

// Componente para recalcular e centralizar o mapa corretamente
function MapFixer({ center }) {
    const map = useMap();

    useEffect(() => {
        // Recalcula o tamanho da div do mapa
        map.invalidateSize();
        
        // Garante centralização precisa no ponto informado
        if (center) {
            map.setView(center, map.getZoom());
        }
    }, [map, center]);

    return null;
}

export default function Map({ marks = [], center = ANHANGUERA_POSITION, zoom = 11 }) {
    return (
        <div className={styles.grafico}>
            <div className={styles.mapWrapper}>
                <MapContainer
                    center={center}
                    zoom={zoom}
                    minZoom={7}
                    maxZoom={16}
                    maxBounds={SAO_PAULO_BOUNDS}
                    maxBoundsViscosity={1}
                    style={{ height: '100%', width: '100%' }}
                >
                    <MapFixer center={center} />

                    <TileLayer
                        noWrap
                        bounds={SAO_PAULO_BOUNDS}
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; OpenStreetMap contributors'
                    />

                    {anhangueraData && (
                        <GeoJSON 
                            data={anhangueraData} 
                            style={ANHANGUERA_STYLE} 
                        />
                    )}

                    {Array.isArray(marks) && marks.map((mark, index) => {
                        if (!mark?.position) return null;

                        return (
                            <CircleMarker
                                key={mark.id || index}
                                center={mark.position}
                                radius={10}
                                pathOptions={{ 
                                    color: 'var(--laranja)', 
                                    fillColor: 'var(--laranja)', 
                                    fillOpacity: 0.35 
                                }}
                            >
                                <Popup>
                                    {mark.information}
                                </Popup>
                            </CircleMarker>
                        );
                    })}
                </MapContainer>
            </div>
        </div>
    );
}