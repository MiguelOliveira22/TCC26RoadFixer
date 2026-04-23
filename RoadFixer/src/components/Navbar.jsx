import { useNavigate } from 'react-router-dom';

export default function Navbar() {
<<<<<<< Updated upstream
  const navigate = useNavigate(); // Hook para navegação
=======
  const links = [
    { label: 'Home', href: '#home' },
    { label: 'Estatisticas', href: '#estatisticas' },
    { label: 'Mapa', href: '#mapa' },
  ];
>>>>>>> Stashed changes

  return (
    <nav style={styles.nav}>
      <h1 
        style={{ ...styles.logo, cursor: 'pointer' }} 
        onClick={() => navigate('/')}
      >
        Road<span style={{color: 'var(--laranja)'}}>Fixer</span>
      </h1>

      <ul style={styles.ul}>
<<<<<<< Updated upstream
        <li style={styles.li} onClick={() => navigate('/')}>
          Home
        </li>

        <li style={styles.li} onClick={() => navigate('/estatisticas')}>
          Estatísticas
        </li>

        <li style={styles.button} onClick={() => navigate('/saibaMais')}>
          Saiba Mais
=======
        {links.map((link) => (
          <li key={link.href}>
            <a href={link.href} style={styles.link}>
              {link.label}
            </a>
          </li>
        ))}
        <li>
          <a href="#relatos" style={styles.button}>Saiba Mais</a>
>>>>>>> Stashed changes
        </li>
      </ul>
    </nav>
  )
}

const styles = {
  nav: {
    position: 'sticky',
    top: 0,
    zIndex: 20,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 5%',
    backgroundColor: 'var(--cinza-escuro)',
    borderBottom: '2px solid var(--laranja)',
    color: 'white' 
  },
  logo: { fontSize: '1.5rem', fontWeight: 'bold' },
<<<<<<< Updated upstream
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
=======
  ul: {
    display: 'flex',
    listStyle: 'none',
    gap: '2rem',
    alignItems: 'center',
    margin: 0,
    padding: 0
  },
  link: {
    cursor: 'pointer',
    fontWeight: '500',
    transition: '0.3s',
    color: 'var(--branco)',
    textDecoration: 'none'
>>>>>>> Stashed changes
  },
  button: {
    display: 'inline-block',
    backgroundColor: 'var(--laranja)',
    color: 'white',
    padding: '0.6rem 1.2rem',
    borderRadius: '4px',
    fontWeight: 'bold',
    cursor: 'pointer',
<<<<<<< Updated upstream
    transition: '0.3s',
    border: 'none' // Garante que não haja borda de botão nativo
=======
    color: 'var(--branco)',
    textDecoration: 'none'
>>>>>>> Stashed changes
  }
}
