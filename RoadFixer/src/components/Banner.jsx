import { useNavigate } from "react-router-dom";
import styles from "./Banner.module.css";

export default function Banner({ 
  title = "SEGURANÇA NAS", 
  highlight = "RODOVIAS", 
  subtitle = "Dados em tempo real e informações cruciais sobre transportes.", 
  buttonText = "Ver Relatórios", 
  linkTo = "/monitoramento"
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
        
        <button 
          className={styles.mainBtn} 
          onClick={() => navigate(linkTo)}
        >
          {buttonText}
        </button>
      </div>
    </section>
  );
}