import { useNavigate } from 'react-router-dom';
import { pathObject } from '../Constants';
import styles from "./Navbar.module.css";
import FilledButton from './Button/FilledButton';
import BaseButton from './Button/BaseButton';

export default function Navbar() {
  const navigate = useNavigate();

  const handleNavigate = (path) => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    navigate(path);
  };

  return (
    <header className={styles.header}>
      <nav className={styles.nav}>
        <h1 className={styles.logo} onClick={() => handleNavigate(pathObject.path)}>
          Road<span className={styles.highlight}>Fixer</span>
        </h1>

        <ul className={styles.menuList}>
          <li>
            <BaseButton 
              className={styles.smallBtn}
              value="Início" 
              action={() => handleNavigate(pathObject.path)} 
            />
          </li>
          <li>
            <BaseButton 
              className={styles.smallBtn}
              value="Monitoramento" 
              action={() => handleNavigate(pathObject.children[0].path)} 
            />
          </li>
          <li>
            <BaseButton 
              className={styles.smallBtn}
              value="Estatísticas" 
              action={() => handleNavigate(pathObject.children[2].path)} 
            />
          </li>
          <li>
            <FilledButton 
              className={styles.smallBtn}
              value="Saiba Mais" 
              action={() => handleNavigate(pathObject.children[1].path)} 
            />
          </li>
        </ul>
      </nav>
    </header>
  );
}