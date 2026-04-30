import CardData from "./cards/CardData";

export default function Stats() {
  const data = [
    { label: "BR 330", value: "Rodovia em Foco" },
    { label: "Acidentes Registrados", value: "1.204 milhões" },
    { label: "Tempo de Resposta", value: "12 min" },
  ];

  return (
    <section id="estatisticas" style={styles.container}>
      <div style={styles.grid}>
        {data.map((item, index) => (
          <CardData label={item.label} value={item.value} key={index}/>
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
