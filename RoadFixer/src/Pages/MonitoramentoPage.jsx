import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function MonitoramentoPage() {
  const position = [-15.7801, -47.9292];

  return (
    <section id="mapa" style={styles.section}>
      <div style={styles.header}>
        <p style={styles.kicker}>VISÃO OPERACIONAL</p>
        <h2 style={styles.title}>MAPA <span style={{ color: 'var(--laranja)' }}>INTERATIVO</span></h2>
        <p style={styles.subtitle}>Tela dedicada para consultar os relatos e visualizar os pontos de atenção no mapa.</p>
      </div>
      <div style={styles.mapWrapper}>
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
    </section>
  );
}

const styles = {
  section: {
    padding: '60px 5% 80px',
    backgroundColor: 'var(--preto)',
  },
  header: {
    maxWidth: '720px',
    marginBottom: '24px',
  },
  kicker: {
    color: 'var(--laranja)',
    letterSpacing: '2px',
    fontSize: '0.8rem',
    marginBottom: '8px',
  },
  title: {
    margin: '0 0 12px',
    fontSize: '2.5rem',
  },
  subtitle: {
    color: '#b7b7b7',
    lineHeight: 1.6,
    margin: 0,
  },
  mapWrapper: {
    height: '600px',
    width: '100%',
    borderRadius: '15px',
    overflow: 'hidden',
    border: '2px solid var(--cinza-escuro)',
  },
};
