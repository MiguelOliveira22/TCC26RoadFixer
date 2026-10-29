import styles from "./DataCollection.module.css";
import ScaffoldButton from "./Button/ScaffoldButton";
import { DatasetTable } from "../components/DataSetTable";
import { useState } from "react";
import { downloadDataset } from "../utils/downloadDataset";

const MAX_LINHAS_PAGINA = 3;

export default function DataCollection({ headers, reports, title, buttonText }) {
    const [openPopup, setOpenPopup] = useState(false);
  const lista = reports ?? [];

  return (
    <section id="relatos" className={styles.section}>
      <h2 className={styles.title}>{title}</h2>
      
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              {headers.map((tbHeader, index) => (
                <th key={index} className={styles.th}>{tbHeader}</th>
              ))}
            </tr>
          </thead>
            <tbody>
              {lista.slice(0, MAX_LINHAS_PAGINA).map((link) => (
                <tr key={link.id} className={styles.tr}>
                {link.data.map((dt, idx) => (
                  <td key={idx} className={styles.td}>
                    {dt && typeof dt === "object" && dt.url != null ? (
                      <ScaffoldButton
                        value={dt.body ? "BAIXAR" : "DETALHES"}
                        action={() =>
                          dt.body
                            ? downloadDataset(dt).catch(console.error)
                            : window.open(dt.url, "_blank")
                        }
                        orange={false}
                        small={true}
                      />
                    ) : (
                      dt
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        {lista.length > MAX_LINHAS_PAGINA && (
          <div className={styles.buttonContainer}>
            <ScaffoldButton
              value={buttonText}
              action={() => setOpenPopup(true)}
              orange={false}
            />
          </div>
        )}

        <DatasetTable
          isOpen={openPopup}
          onClose={() => setOpenPopup(false)}
          headers={headers}
          title={title}
          datasets={lista}
        />
      </div>
    </section>
  );
}