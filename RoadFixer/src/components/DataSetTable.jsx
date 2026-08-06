import styles from "./DataSetTable.module.css";
import ScaffoldButton from "./Button/ScaffoldButton";

export function DatasetTable({ isOpen, onClose, headers, title, datasets }) {
  if (!isOpen) return null;

  return (
    <div className={styles.datasetOverlay} onClick={onClose}>
      <div
        className={styles.datasetModal}
        onClick={(e) => e.stopPropagation()}
      >
        <button className={styles.datasetBackBtn} onClick={onClose}>
          ← VOLTAR
        </button>

        <h1 className={styles.datasetTitle}>{title}</h1>

        <div className={styles.tableScroll}>
          <table className={styles.datasetTable}>
            <thead>
              <tr className={styles.datasetHeader}>
                {headers.map((header, index) => (
                  <th key={index} className={styles.th}>
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {datasets.map((item) => (
                <tr key={item.id} className={styles.datasetRow}>
                  {item.data.map((dt, idx) => (
                    <td key={idx} className={styles.td}>
                      {typeof dt === "string" ? (
                        dt
                      ) : (
                        <ScaffoldButton
                          value="Detalhes"
                          action={() => window.open(dt.url, "_blank")}
                          orange={false}
                          small={true}
                        />
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}