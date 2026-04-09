// components/Footer.jsx
export default function Footer() {
  return (
    <footer style={styles.footer}>
      <div style={styles.top}>
        <div>
          <h2 style={{margin: 0}}>ACIDENTES<span style={{color: 'var(--laranja)'}}>UAU</span></h2>
          <p style={{color: '#666'}}>Dados que salvam vidas nas estradas brasileiras.</p>
        </div>
        <div style={styles.links}>
          <span>Privacidade</span>
          <span>Termos</span>
          <span>Contato</span>
        </div>
      </div>
      <div style={styles.bottom}>
        © 2026 - Desenvolvido com foco em segurança rodoviária.
      </div>
    </footer>
  );
}

const styles = {
  footer: {
    backgroundColor: '#000',
    padding: '60px 5% 20px 5%',
    borderTop: '1px solid #222'
  },
  top: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '40px',
    flexWrap: 'wrap',
    gap: '20px'
  },
  links: { display: 'flex', gap: '30px', color: '#888', fontSize: '0.9rem' },
  bottom: {
    textAlign: 'center',
    color: '#444',
    fontSize: '0.8rem',
    borderTop: '1px solid #111',
    paddingTop: '20px'
  }
};