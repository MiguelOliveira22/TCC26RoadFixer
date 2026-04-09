// components/Features.jsx
export default function Features() {
  const cards = [
    { title: "Monitoramento", desc: "Câmeras ao vivo e sensores de pista 24h." },
    { title: "Alertas", desc: "Notificações de acidentes e bloqueios imediatos." },
    { title: "Histórico", desc: "Base de dados completa desde 2020." }
  ];

  return (
    <section style={styles.section}>
      <h2 style={styles.title}>NOSSO <span style={{color: 'var(--laranja)'}}>FOCO</span></h2>
      <div style={styles.grid}>
        {cards.map((card, i) => (
          <div key={i} style={styles.card} className="feature-card">
            <h3 style={{color: 'var(--laranja)'}}>{card.title}</h3>
            <p>{card.desc}</p>
            <div style={styles.link}>Ver mais →</div>
          </div>
        ))}
      </div>
    </section>
  );
}

const styles = {
  section: { padding: '80px 5%', backgroundColor: 'var(--preto)' },
  title: { fontSize: '2.5rem', marginBottom: '40px', textAlign: 'center' },
  grid: { display: 'flex', gap: '20px', flexWrap: 'wrap' },
  card: {
    flex: 1,
    minWidth: '300px',
    padding: '40px',
    border: '1px solid #333',
    transition: '0.3s ease',
    cursor: 'pointer',
    backgroundColor: 'var(--cinza-escuro)'
  },
  link: { marginTop: '20px', fontWeight: 'bold', fontSize: '0.9rem' }
};