import { useNavigate } from 'react-router-dom';
import styles from './Navbar.module.css';

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav className={styles.nav}>
      <h1 
        className={styles.logo} 
        onClick={() => navigate('/')}
      >
        Road<span className={styles.highlight}>Fixer</span>
      </h1>

      <ul className={styles.ul}>
        <li className={styles.li} onClick={() => navigate('/')}>
          Home
        </li>

        <li className={styles.li} onClick={() => navigate('/estatisticas')}>
          Estatísticas
        </li>

        <li className={styles.button} onClick={() => navigate('/saiba-mais')}>
          Saiba Mais
        </li>
      </ul>
    </nav>
  );
}