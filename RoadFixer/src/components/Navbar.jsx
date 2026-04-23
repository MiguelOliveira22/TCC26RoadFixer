import { useNavigate } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate(); // Hook para navegação

  return (
    <nav style={styles.nav}>
      <h1 
        style={{ ...styles.logo, cursor: 'pointer' }} 
        onClick={() => navigate('/')}
      >
        Road<span style={{color: 'var(--laranja)'}}>Fixer</span>
      </h1>

      <ul style={styles.ul}>
        <li style={styles.li} onClick={() => navigate('/')}>
          Home
        </li>

        <li style={styles.li} onClick={() => navigate('/estatisticas')}>
          Estatísticas
        </li>

        <li style={styles.button} onClick={() => navigate('/saibaMais')}>
          Saiba Mais
        </li>
      </ul>
    </nav>
  )
}

const styles = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 5%',
    backgroundColor: 'var(--cinza-escuro)',
    borderBottom: '2px solid var(--laranja)',
    color: 'white' 
  },
  logo: { fontSize: '1.5rem', fontWeight: 'bold' },
  ul: { 
    display: 'flex', 
    listStyle: 'none', 
    gap: '2rem', 
    alignItems: 'center',
    margin: 0,
    padding: 0 
  },
  li: { 
    cursor: 'pointer', 
    fontWeight: '500', 
    transition: '0.3s' 
  },
  button: {
    backgroundColor: 'var(--laranja)',
    color: 'white',
    padding: '0.6rem 1.2rem',
    borderRadius: '4px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: '0.3s',
    border: 'none' // Garante que não haja borda de botão nativo
  }
}