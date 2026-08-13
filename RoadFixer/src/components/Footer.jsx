import { useNavigate } from "react-router-dom";
import styles from "./Footer.module.css";

export default function Footer() {
  const navigate = useNavigate();

  const handleInternalNav = (path) => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    navigate(path);
  };

  const linksSaibaMais = [
    { text: "Estatísticas", action: () => handleInternalNav('/estatisticas') },
    { text: "Site Concessionária", url: 'https://www.rodoviaanhanguera.com.br/' },
    { text: "Coletânea de Pesquisas Utilizadas", url: 'https://drive.google.com/drive/folders/1DTl53Iwic3K--vYx8XcfTfrC53YAajas?usp=sharing' },
    { text: "ARTESP Dados Abertos", url: 'https://dadosabertos.artesp.sp.gov.br/' },
    { text: "DER Dados Abertos", url: 'https://www.der.sp.gov.br/WebSite/Servicos/DadosAbertos.aspx' },
  ];

  const emails = [
    "migueloqueiroz@gmail.com",
    "henriqueinoue1000@gmail.com",
    "ggermano@gmail.com",
    "matheuscalopsita36@gmail.com"
  ];

  return (
    <footer className={styles.footer}>
      <div className={styles.topSection}>
        
        {/* Coluna 1: Objetivo */}
        <div className={styles.column}>
          <h3 className={styles.columnTitle}>
            NOSSO <span className={styles.highlight}>OBJETIVO</span>
          </h3>
          <p className={styles.objectiveText}>
            Utilizar modelos probabilísticos para determinar riscos de acidentes 
            e propor soluções preventivas autônomas nas rodovias.
          </p>
        </div>

        <div className={styles.divider}></div> 

        {/* Coluna 2: Saiba Mais */}
        <div className={styles.column}>
          <h3 className={styles.columnTitle}>SAIBA MAIS</h3>
          <ul className={styles.list}>
            {linksSaibaMais.map((link, index) => (
              <li key={index} className={styles.listItem}>
                {link.url ? (
                  <a 
                    href={link.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className={styles.link}
                  >
                    {link.text} <span className={styles.externalIcon}>↗</span>
                  </a>
                ) : (
                  <button 
                    onClick={link.action} 
                    className={styles.linkButton}
                  >
                    {link.text}
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div className={styles.divider}></div> 

        {/* Coluna 3: Contato */}
        <div className={styles.column}>
          <h3 className={styles.columnTitle}>CONTATO</h3>
          <div className={styles.emailList}>
            {emails.map((email, index) => (
              <a 
                key={index} 
                href={`mailto:${email}`} 
                className={styles.emailLink}
              >
                {email}
              </a>
            ))}
          </div>
        </div>

      </div>

      <div className={styles.bottomSection}>
        <span className={styles.copyright}>
          © 2026 - <span className={styles.brandName}>RoadFixer</span> - Todos os direitos reservados.
        </span>
      </div>
    </footer>
  );
}