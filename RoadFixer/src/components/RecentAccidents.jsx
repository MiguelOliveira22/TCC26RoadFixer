import { useNavigate } from "react-router-dom";
import styles from "./RecentAccidents.module.css";

export default function RecentAccidents() {
  const navigate = useNavigate();

  const reports = [
    { id: 1, local: "BR-116 KM 240", status: "Bloqueado", gravidade: "Alta" },
    { id: 2, local: "BR-101 KM 012", status: "Liberado", gravidade: "Baixa" },
    { id: 3, local: "BR-381 KM 480", status: "Atenção", gravidade: "Média" },
  ];

  return (
    <section id="relatos" className={styles.section}>
      <h2 className={styles.title}>
        ÚLTIMOS <span className={styles.highlight}>RELATOS</span>
      </h2>
      
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>LOCALIZAÇÃO</th>
              <th className={styles.th}>STATUS</th>
              <th className={styles.th}>GRAVIDADE</th>
              <th className={styles.th}>AÇÃO</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.id} className={styles.tr}>
                <td className={styles.td}>{r.local}</td>
                <td className={styles.td}>
                  <span className={`${styles.badge} ${r.status === 'Bloqueado' ? styles.blocked : ''}`}>
                    ● {r.status}
                  </span>
                </td>
                <td className={styles.td}>{r.gravidade}</td>
                <td className={styles.td}>
                  <button 
                    className={styles.miniBtn} 
                    onClick={() => navigate('/monitoramento')}
                  >
                    DETALHES
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}