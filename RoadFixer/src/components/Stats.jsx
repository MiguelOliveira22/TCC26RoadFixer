export default function Stats() {
  const data = [
    { label: "Rodovias Monitoradas", value: "Todas" },
    { label: "Acidentes Registrados", value: "1.204 milhões" },
    { label: "Transportes Ativos", value: "45.000+" },
    { label: "Tempo de Resposta", value: "12 min" },
  ];

  return (
    <section id="estatisticas" style={styles.container}>
      <div style={styles.grid}>
        {data.map((item, index) => (
          <div key={index} style={styles.card}>
            <div style={styles.accent}></div>
            <h3 style={styles.value}>{item.value}</h3>
            <p style={styles.label}>{item.label}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

const styles = {
  container: {
    padding: '60px 5%',
    backgroundColor: 'var(--preto)',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
  },
  card: {
    backgroundColor: 'var(--cinza-escuro)',
    padding: '30px',
    borderRadius: '8px',
    textAlign: 'center',
    position: 'relative',
    overflow: 'hidden',
    border: '1px solid #333',
  },
  accent: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '4px',
    backgroundColor: 'var(--laranja)',
  },
  value: {
    fontSize: '2.5rem',
    margin: '10px 0',
    color: 'var(--branco)',
    fontWeight: 'bold',
  },
  label: {
    color: '#888',
    textTransform: 'uppercase',
    fontSize: '0.8rem',
    letterSpacing: '1px',
  }
};
