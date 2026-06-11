import { useNavigate } from 'react-router-dom';
import { pathObject } from '../Constants';
import styles from "./Navbar.module.css";
import FilledButton from './Button/FilledButton';
import BaseButton from './Button/BaseButton';

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav className={styles.nav}>
      <h1 className={styles.logo} onClick={() => navigate(pathObject.path)}>
        Road<span className={styles.highlight}>Fixer</span>
      </h1>

      <ul className={styles.ul}>
        <BaseButton value={ "Inicio" } action={ () => {
          window.scrollTo(0, 0);
          navigate(pathObject.path);
        }}/>

        <BaseButton value={ "Monitoramento" } action={ () => {
          window.scrollTo(0, 0);
          navigate(pathObject.children[0].path);
        }}/>

        <BaseButton value={ "Estatísticas" } action={ () => {
          window.scrollTo(0, 0);
          navigate(pathObject.children[2].path);
        }}/>

        <FilledButton value={ "Saiba Mais" } action={ () => {
          window.scrollTo(0, 0);
          navigate(pathObject.children[1].path);
        } }/>
      </ul>
    </nav>
  )
}
