import { useNavigate } from "react-router-dom";
import styles from "./DataCollection.module.css";
import ScaffoldButton from "./Button/ScaffoldButton";

export default function RecentAccidents() {
  const navigate = useNavigate();

  // Não temos url para os tipos de dados que ainda coletaremos
  const reports = [
    { id: 1, dado: "Clima" , url: ""},
    { id: 2, dado: "Topologia" , url: ""},
    { id: 3, dado: "Estrutura física da pista" , url: ""},
  ];

  return (
    <section id="relatos" className={styles.section}>
      <h2 className={styles.title}>
        CONJUNTO DE <span className={styles.highlight}>DADOS UTILIZADOS</span>
      </h2>
      
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>DADO</th>
              <th className={styles.th}>LINK</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.id} className={styles.tr}>
                <td className={styles.td}>{r.dado}</td>
                <td className={styles.td}>
                  <button 
                    className={styles.miniBtn} 
                    onClick={() => window.open(r.url, '_blank')}
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