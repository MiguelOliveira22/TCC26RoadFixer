import { useNavigate } from "react-router-dom";
import styles from "./Footer.module.css";

export default function Footer() {
  const navigate = useNavigate();

  const linksSaibaMais = [
    { text: "Estatísticas", action: () => { window.scrollTo(0, 0); navigate('/estatisticas'); } },
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

  // Função para abrir o cliente de e-mail
  const handleEmailClick = (email) => {
    window.location.href = `mailto:${email}`;
  };

  return (
    <footer className={styles.footer}>
      <div className={styles.topSection}>
        
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

        <div className={styles.column}>
          <h3 className={styles.columnTitle}>SAIBA MAIS</h3>
          <ul className={styles.list}>
            {linksSaibaMais.map((link, index) => (
              <li 
                key={index} 
                className={styles.listItem} 
                onClick={link.url ? () => window.open(link.url, '_blank') : link.action}
              >
                {link.text}
              </li>
            ))}
          </ul>
        </div>

        <div className={styles.divider}></div> 

        <div className={styles.column}>
          <h3 className={styles.columnTitle}>CONTATO</h3>
          <div className={styles.emailList}>
            {emails.map((email, index) => (
              <span 
                key={index} 
                className={styles.email} 
                onClick={() => handleEmailClick(email)}
                style={{ cursor: 'pointer' }} // Garante que o cursor de "mãozinha" apareça ao passar o mouse
              >
                {email}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className={styles.bottomSection}>
        <span className={styles.copyright}>
          © 2026 - RoadFixer - Todos os direitos reservados.
        </span>
      </div>
    </footer>
  );
}