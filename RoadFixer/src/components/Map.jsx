import { useEffect, useMemo } from 'react';
import { CircleMarker, MapContainer, Popup, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import { buildRiskSegments, riskColor } from '../utils/buildRiskSegments';
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

export default function Map({ risk = [], marks = [], center = ANHANGUERA_POSITION, zoom = 11 }) {
    const riskValues = useMemo(
        () => risk.map((r) => (typeof r === "number" ? r : r.risco)),
        [risk]
    );

    const segments = useMemo(
        () => buildRiskSegments(anhangueraData, riskValues),
        [riskValues]
    );

    const geoKey = useMemo(() => riskValues.join(","), [riskValues]);
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
                        url="https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_4cxu_1_bcf48748192f648ed948b64a" // Alterar depois para um proxy
                        attribution="&copy; CARTO"
                    />

                    {anhangueraData && (
                            <GeoJSON
                                key={geoKey}
                                data={segments}
                                style={(feature) => ({
                                    color: riskColor(feature.properties.risco),
                                    weight: 5,
                                    opacity: 0.95,
                                    lineCap: "round",
                                })}
                                onEachFeature={(feature, layer) => {
                                    layer.bindTooltip(`km ${feature.properties.km} · risco ${Number(feature.properties.risco).toFixed(2)}`);
                                }}
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