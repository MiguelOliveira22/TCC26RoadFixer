import { useNavigate } from "react-router-dom";
import styles from "./Banner.module.css";
import { pathObject } from "../Constants";
import ScaffoldButton from "./Button/ScaffoldButton";

export default function Banner({ 
  title = "SEGURANÇA NAS", 
  highlight = "RODOVIAS", 
  subtitle = "Dados em tempo real e informações cruciais sobre transportes.", 
  buttonText = "Ver Relatórios", 
  linkTo = pathObject.children[2].path
}) {
  const navigate = useNavigate();

  

  return (
    <section id="home" className={styles.hero}>
      <div className={styles.content}>
        <h2 className={styles.title}>
          {title} <br/> 
          <span className={styles.highlight}>{highlight}</span>
        </h2>
        <p className={styles.subtitle}>{subtitle}</p>
        
        <ScaffoldButton value={buttonText} action={() => {
          window.scrollTo(0, 0);
          navigate(linkTo);
        }} orange/>
      </div>
      <div className={styles.rights}>
        <p>Foto por <span className={styles.bold}>Aderlei de Souza</span></p>
      </div>
    </section>
  );
}