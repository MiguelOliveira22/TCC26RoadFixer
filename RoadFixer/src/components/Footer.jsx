import { useNavigate } from "react-router-dom";

export default function Footer() {
  const navigate = useNavigate();

  return (
    <footer style={styles.footer}>
      <div style={styles.topSection}>
        
        <div style={styles.column}>
          <h3 style={styles.columnTitle}>
            NOSSO <span style={{ color: "var(--laranja)" }}>OBJETIVO</span>
          </h3>
          <p style={styles.objectiveText}>
            Utilizar modelos probabilísticos para determinar riscos de acidentes 
            e propor soluções preventivas autônomas nas rodovias.
          </p>
        </div>

        <div style={styles.divider}></div> 

        <div style={styles.column}>
          <h3 style={styles.columnTitle}>SAIBA MAIS</h3>
          <ul style={styles.list}>
            <li style={styles.listItem} onClick={() => navigate('/estatisticas')}>Estatísticas</li>

            <li style={styles.listItem} onClick={() => window.open('https://www.rodoviaanhanguera.com.br/', '_blank')}>
              Site Concessionária
            </li>

            <li style={styles.listItem} onClick={() => window.open('https://link-das-pesquisas.com', '_blank')}>
              Coletânea de Pesquisas Utilizadas
            </li>

            <li style={styles.listItem} onClick={() => window.open('https://dadosabertos.artesp.sp.gov.br/', '_blank')}>
              ARTESP Dados Abertos
            </li>

            <li style={styles.listItem} onClick={() => window.open('https://www.der.sp.gov.br/WebSite/Servicos/DadosAbertos.aspx', '_blank')}>
              DER Dados Abertos
            </li>
          </ul>
        </div>

        <div style={styles.divider}></div> 


        <div style={styles.column}>
          <h3 style={styles.columnTitle}>CONTATO</h3>
          <div style={styles.emailList}>
            <span style={styles.email}>migueloqueiroz@gmail.com</span>
            <span style={styles.email}>henriqueinoue1000@gmail.com</span>
            <span style={styles.email}>ggermano@gmail.com</span>
            <span style={styles.email}>matheuscalopsita36@gmail.com</span>
          </div>
        </div>
      </div>

      <div style={styles.bottomSection}>
        <span style={styles.copyright}>
          © 2026 - RoadFixer - Todos os direitos reservados.
        </span>
      </div>
    </footer>
  );
}

const styles = {
  footer: {
    backgroundColor: "var(--cinza-escuro)",
    color: "white",
    padding: "4rem 5% 2rem",
    borderTop: "1px solid #222",
  },
  topSection: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "stretch",
    gap: "20px",
    marginBottom: "3rem",
    flexWrap: "wrap",
  },
  column: {
    flex: "1",
    minWidth: "250px",
    padding: "0 15px",
  },
  divider: {
    width: "1px",
    backgroundColor: "#333", 
    margin: "10px 0",
  },
  columnTitle: { 
    fontSize: "1.1rem",
    fontWeight: "bold",
    marginBottom: "1.5rem",
    letterSpacing: "1px",
  },
  objectiveText: {
    fontSize: "0.9rem",
    color: "#aaa",
    lineHeight: "1.6",
  },
  list: {
    listStyle: "none",
    padding: 0,
    margin: 0,
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  listItem: {
    fontSize: "0.9rem",
    color: "#aaa",
    cursor: "pointer",
  },
  emailList: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  email: {
    fontSize: "0.9rem",
    color: "#aaa",
  },
  bottomSection: {
    borderTop: "1px solid #333",
    paddingTop: "2rem",
    textAlign: "center",
  },
  copyright: {
    fontSize: "0.8rem",
    color: "#555",
  },
};