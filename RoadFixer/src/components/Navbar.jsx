import { useNavigate } from 'react-router-dom';
import { pathObject } from '../Constants';
import styles from "./Navbar.module.css";
import FilledButton from './Button/FilledButton';

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav className={styles.nav}>
      <h1 
        className={styles.logo} 
        onClick={() => navigate(pathObject.path)}
      >
        Road<span className={styles.highlight}>Fixer</span>
      </h1>

      <ul className={styles.ul}>
        <li className={styles.li} onClick={() => {
          window.scrollTo(0, 0)
          navigate(pathObject.path)
          }}>
          Inicio
        </li>

        <li className={styles.li} onClick={() => {
          window.scrollTo(0, 0)
          navigate(pathObject.children[0].path)
          }}>
          Estatísticas
        </li>

        <li className={styles.li} onClick={() => {
          window.scrollTo(0, 0)
          navigate(pathObject.children[2].path)
          }}>
          Monitoramento
        </li>

        <FilledButton value={ "Saiba Mais" } action={ () => {
          window.scrollTo(0, 0)
          navigate(pathObject.children[1].path)
          } }/>
      </ul>
    </nav>
  )
}
