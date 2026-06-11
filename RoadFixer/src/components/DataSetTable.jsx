// DataSetTable.jsx
import styles from "./DataSetTable.module.css";
import ScaffoldButton from "./Button/ScaffoldButton";

export function DatasetTable({ isOpen, onClose, headers, title, datasets  }) {
  if (!isOpen) return null;

  datasets.map((item) => {
      item.data.map((obj) =>{
        console.log(typeof(obj))
      })
  })  

  return (
    <div className={styles.datasetOverlay} onClick={onClose}>
      <div
        className={styles.datasetModal}
        onClick={(e) => e.stopPropagation()}
      >
        <button className={styles.datasetBackBtn} onClick={onClose}>
          ← VOLTAR
        </button>

        <h1 className={styles.datasetTitle}>
          {title}
        </h1>

        <table className={styles.datasetTable}>
          <thead className={styles.datasetHeader}>
            {
              headers.map((header) => (
                <div className={styles.divTable}>
                  <th className={styles.th}> {header} </th>
                </div>
              ))
            }
          </thead>

          {datasets.map((item) => (
            <tr className={styles.datasetRow}>
              {
                item.data.map((string) =>
                  typeof(string) == "string" ?
                  <div className={styles.divTable}>
                    <td>{string}</td>
                  </div>
                  :
                  <div className={styles.divTable}>
                    <ScaffoldButton
                    value = {"Detalhes"}
                    action = {() => window.open(string.url, '_blank')}
                    orange = {false}
                    />
                </div>
                )
              }
              <td>
                
              </td>
            </tr>
          ))}
        </table>
      </div>
    </div>
  );
}