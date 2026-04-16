import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function MapaPage() {
  const position = [-15.7801, -47.9292];

  return (
    <div style={{ padding: '100px 5% 50px', minHeight: '100vh', backgroundColor: 'var(--preto)' }}>
      <h1 style={{ color: 'var(--laranja)', marginBottom: '20px' }}>MAPA INTERATIVO</h1>
      <div style={{ height: '600px', width: '100%', borderRadius: '15px', overflow: 'hidden', border: '2px solid var(--cinza-escuro)' }}>
        <MapContainer center={position} zoom={4} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; OpenStreetMap contributors'
          />
          <Marker position={[-23.5505, -46.6333]}>
            <Popup>Incidente detectado em SP.</Popup>
          </Marker>
        </MapContainer>
      </div>
    </div>
  );
}