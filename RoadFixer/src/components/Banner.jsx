// components/Banner.jsx
export default function Banner() {
  return (
    <section style={styles.hero}>
      <div style={styles.content}>
        <h2 style={styles.title}>SEGURANÇA NAS <br/> <span style={{color: 'var(--laranja)'}}>RODOVIAS</span></h2>
        <p style={styles.subtitle}>Dados em tempo real e informações cruciais sobre transportes.</p>
        <button style={styles.mainBtn}>Ver Relatórios</button>
      </div>
    </section>
  )
}

const styles = {
  hero: {
    height: '80vh',
    display: 'flex',
    alignItems: 'center',
    padding: '0 5%',
    background: 'linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1510511459019-5dee995d3ff4?auto=format&fit=crop&q=80&w=2070") shadow',
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  },
  title: { fontSize: '4rem', margin: 0, lineHeight: '1.1' },
  subtitle: { fontSize: '1.2rem', color: '#ccc', margin: '20px 0' },
  mainBtn: {
    padding: '1rem 2rem',
    fontSize: '1rem',
    backgroundColor: 'transparent',
    border: '2px solid var(--laranja)',
    color: 'var(--laranja)',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: '0.4s'
  }
}