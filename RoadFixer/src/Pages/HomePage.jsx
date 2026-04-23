import { Link } from "react-router-dom";

export default function HomePage() {
  const stats = [
    { label: "Rodovias Monitoradas", value: "Todas" },
    { label: "Acidentes Registrados", value: "1.204 milhões" },
    { label: "Transportes Ativos", value: "45.000+" },
    { label: "Tempo de Resposta", value: "12 min" },
  ];

  const features = [
    { title: "Monitoramento", desc: "Câmeras ao vivo e sensores de pista 24h." },
    { title: "Alertas", desc: "Notificações de acidentes e bloqueios imediatos." },
    { title: "Histórico", desc: "Base de dados completa desde 2020." },
  ];

  const reports = [
    { id: 1, local: "BR-116 KM 240", status: "Bloqueado", gravidade: "Alta" },
    { id: 2, local: "BR-101 KM 012", status: "Liberado", gravidade: "Baixa" },
    { id: 3, local: "BR-381 KM 480", status: "Atenção", gravidade: "Média" },
  ];

  return (
    <>
      <nav style={styles.nav}>
        <h1 style={styles.logo}>
          Road<span style={{ color: "var(--laranja)" }}>Fixer</span>
        </h1>
        <ul style={styles.navList}>
          <li>
            <a href="#home" style={styles.navLink}>Home</a>
          </li>
          <li>
            <a href="#estatisticas" style={styles.navLink}>Estatisticas</a>
          </li>
          <li>
            <a href="#relatos" style={styles.navButton}>Saiba Mais</a>
          </li>
        </ul>
      </nav>

      <main>
        <section id="home" style={styles.hero}>
          <div style={styles.heroContent}>
            <h2 style={styles.heroTitle}>
              SEGURANÇA NAS <br />
              <span style={{ color: "var(--laranja)" }}>RODOVIAS</span>
            </h2>
            <p style={styles.heroSubtitle}>
              Dados em tempo real e informações cruciais sobre transportes.
            </p>
            <Link to="/mapa" style={styles.heroButton}>Ver Relatórios</Link>
          </div>
        </section>

        <section id="estatisticas" style={styles.statsSection}>
          <div style={styles.statsGrid}>
            {stats.map((item) => (
              <div key={item.label} style={styles.statCard}>
                <div style={styles.statAccent}></div>
                <h3 style={styles.statValue}>{item.value}</h3>
                <p style={styles.statLabel}>{item.label}</p>
              </div>
            ))}
          </div>
        </section>

        <section style={styles.featuresSection}>
          <h2 style={styles.sectionTitle}>
            NOSSO <span style={{ color: "var(--laranja)" }}>FOCO</span>
          </h2>
          <div style={styles.featuresGrid}>
            {features.map((card) => (
              <div key={card.title} style={styles.featureCard} className="feature-card">
                <h3 style={styles.featureTitle}>{card.title}</h3>
                <p style={styles.featureText}>{card.desc}</p>
                <div style={styles.featureLink}>Ver mais →</div>
              </div>
            ))}
          </div>
        </section>

        <section id="relatos" style={styles.reportsSection}>
          <h2 style={styles.reportsTitle}>
            ÚLTIMOS <span style={{ color: "var(--laranja)" }}>RELATOS</span>
          </h2>
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>LOCALIZAÇÃO</th>
                  <th style={styles.th}>STATUS</th>
                  <th style={styles.th}>GRAVIDADE</th>
                  <th style={styles.th}>AÇÃO</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id} style={styles.tr}>
                    <td style={styles.td}>{report.local}</td>
                    <td style={styles.td}>
                      <span
                        style={{
                          ...styles.badge,
                          color: report.status === "Bloqueado" ? "var(--laranja)" : "#fff",
                        }}
                      >
                        ● {report.status}
                      </span>
                    </td>
                    <td style={styles.td}>{report.gravidade}</td>
                    <td style={styles.td}>
                      <Link to="/mapa" style={styles.miniBtn}>DETALHES</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      <footer style={styles.footer}>
        <div style={styles.footerTop}>
          <div style={styles.footerLinks}>
            <a href="#home" style={styles.footerLink}>Home</a>
            <a href="#estatisticas" style={styles.footerLink}>Estatisticas</a>
            <Link to="/mapa" style={styles.footerLink}>Mapa</Link>
          </div>
        </div>
        <div style={styles.footerBottom}>
          © 2026 - Desenvolvido com foco em segurança rodoviária.
        </div>
      </footer>
    </>
  );
}

const styles = {
  nav: {
    position: "sticky",
    top: 0,
    zIndex: 20,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "1rem 5%",
    backgroundColor: "var(--cinza-escuro)",
    borderBottom: "2px solid var(--laranja)",
  },
  logo: {
    fontSize: "1.5rem",
    fontWeight: "bold",
    margin: 0,
  },
  navList: {
    display: "flex",
    listStyle: "none",
    gap: "2rem",
    alignItems: "center",
    margin: 0,
    padding: 0,
  },
  navLink: {
    color: "var(--branco)",
    textDecoration: "none",
    fontWeight: "500",
  },
  navButton: {
    display: "inline-block",
    backgroundColor: "var(--laranja)",
    padding: "0.6rem 1.2rem",
    borderRadius: "4px",
    fontWeight: "bold",
    color: "var(--branco)",
    textDecoration: "none",
  },
  hero: {
    minHeight: "80vh",
    display: "flex",
    alignItems: "center",
    padding: "0 5%",
    background:
      'linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1510511459019-5dee995d3ff4?auto=format&fit=crop&q=80&w=2070")',
    backgroundSize: "cover",
    backgroundPosition: "center",
  },
  heroContent: {
    maxWidth: "680px",
  },
  heroTitle: {
    fontSize: "4rem",
    margin: 0,
    lineHeight: "1.1",
  },
  heroSubtitle: {
    fontSize: "1.2rem",
    color: "#ccc",
    margin: "20px 0",
  },
  heroButton: {
    display: "inline-block",
    padding: "1rem 2rem",
    fontSize: "1rem",
    backgroundColor: "transparent",
    border: "2px solid var(--laranja)",
    color: "var(--laranja)",
    fontWeight: "bold",
    textDecoration: "none",
  },
  statsSection: {
    padding: "60px 5%",
    backgroundColor: "var(--preto)",
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "20px",
  },
  statCard: {
    backgroundColor: "var(--cinza-escuro)",
    padding: "30px",
    borderRadius: "8px",
    textAlign: "center",
    position: "relative",
    overflow: "hidden",
    border: "1px solid #333",
  },
  statAccent: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "4px",
    backgroundColor: "var(--laranja)",
  },
  statValue: {
    fontSize: "2.5rem",
    margin: "10px 0",
    color: "var(--branco)",
    fontWeight: "bold",
  },
  statLabel: {
    color: "#888",
    textTransform: "uppercase",
    fontSize: "0.8rem",
    letterSpacing: "1px",
  },
  featuresSection: {
    padding: "80px 5%",
    backgroundColor: "var(--preto)",
  },
  sectionTitle: {
    fontSize: "2.5rem",
    marginBottom: "40px",
    textAlign: "center",
  },
  featuresGrid: {
    display: "flex",
    gap: "20px",
    flexWrap: "wrap",
  },
  featureCard: {
    flex: 1,
    minWidth: "300px",
    padding: "40px",
    border: "1px solid #333",
    transition: "0.3s ease",
    cursor: "pointer",
    backgroundColor: "var(--cinza-escuro)",
  },
  featureTitle: {
    color: "var(--laranja)",
  },
  featureText: {
    margin: 0,
  },
  featureLink: {
    marginTop: "20px",
    fontWeight: "bold",
    fontSize: "0.9rem",
  },
  reportsSection: {
    padding: "60px 5%",
    backgroundColor: "var(--preto)",
  },
  reportsTitle: {
    fontSize: "2rem",
    marginBottom: "30px",
  },
  tableWrapper: {
    overflowX: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    color: "#fff",
  },
  th: {
    textAlign: "left",
    padding: "15px",
    borderBottom: "2px solid var(--laranja)",
    color: "#888",
    fontSize: "0.8rem",
  },
  tr: {
    borderBottom: "1px solid #222",
    transition: "0.3s",
  },
  td: {
    padding: "15px",
  },
  badge: {
    fontSize: "0.8rem",
    fontWeight: "bold",
  },
  miniBtn: {
    display: "inline-block",
    backgroundColor: "transparent",
    border: "1px solid #444",
    color: "#fff",
    padding: "5px 10px",
    fontSize: "0.7rem",
    textDecoration: "none",
  },
  footer: {
    backgroundColor: "#000",
    padding: "60px 5% 20px 5%",
    borderTop: "1px solid #222",
  },
  footerTop: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "40px",
    flexWrap: "wrap",
    gap: "20px",
  },
  footerLinks: {
    display: "flex",
    gap: "30px",
    color: "#888",
    fontSize: "0.9rem",
  },
  footerLink: {
    color: "#888",
    textDecoration: "none",
  },
  footerBottom: {
    textAlign: "center",
    color: "#444",
    fontSize: "0.8rem",
    borderTop: "1px solid #111",
    paddingTop: "20px",
  },
};
