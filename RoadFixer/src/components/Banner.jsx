import { useNavigate } from "react-router-dom";
import styles from "./Banner.module.css"

export default function Banner() {
  const navigate = useNavigate();

  return (
    <section id="home" className={styles.hero}>
      <div className={styles.content}>
        <h2 className={styles.title}>SEGURANÇA NAS <br/> <span className={{color: 'var(--laranja)'}}>RODOVIAS</span></h2>
        <p className={styles.subtitle}>Dados em tempo real e informações cruciais sobre transportes.</p>
        
        <button 
          className={styles.mainBtn} 
          onClick={() => navigate('/mapa')}
        >
          Ver Relatórios
        </button>
      </div>
    </section>
  );
}
