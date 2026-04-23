import { useNavigate } from "react-router-dom";

export default function Footer() {
  const navigate = useNavigate();

  return (
    <footer style={styles.footer}>
      <div style={styles.top}>
        <div style={styles.links}>
          <span style={styles.link} onClick={() => navigate('/')}>Home</span>
          <span style={styles.link} onClick={() => navigate('/mapa')}>Mapa</span>
          <span style={styles.link} onClick={() => navigate('/saibaMais')}>Saiba Mais</span>
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
  link: { color: '#888', textDecoration: 'none', cursor: 'pointer' },
  bottom: {
    textAlign: 'center',
    color: '#444',
    fontSize: '0.8rem',
    borderTop: '1px solid #111',
    paddingTop: '20px'
  }
};
