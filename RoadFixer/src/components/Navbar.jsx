export default function Navbar() {
  return (
    <nav style={styles.nav}>
      <h1 style={styles.logo}>Road<span style={{color: 'var(--laranja)'}}>Fixer</span></h1>
      <ul style={styles.ul}>
        <li style={styles.li}>Home</li>
        <li style={styles.li}>Estatísticas</li>
        <li style={styles.button}>Saiba Mais</li>
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
    borderBottom: '2px solid var(--laranja)'
  },
  logo: { fontSize: '1.5rem', fontWeight: 'bold' },
  ul: { display: 'flex', listStyle: 'none', gap: '2rem', alignItems: 'center' },
  li: { cursor: 'pointer', fontWeight: '500', transition: '0.3s' },
  button: {
    backgroundColor: 'var(--laranja)',
    padding: '0.6rem 1.2rem',
    borderRadius: '4px',
    fontWeight: 'bold',
    cursor: 'pointer'
  }
}