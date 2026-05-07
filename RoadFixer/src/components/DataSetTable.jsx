// DataSetTable.jsx
import styles from "./DataSetTable.module.css";
import ScaffoldButton from "./Button/ScaffoldButton";

const datasets = [
  {id: 1, data: "Clima", url: ""},
  {id: 2, data: "Topologia", url: ""},
  {id: 3, data: "Estrutura Física Da Pista", url: ""},
  {id: 4, data: "Conjunto", url: ""},
  {id: 5, data: "Conjunto", url: ""},
  {id: 6, data: "Conjunto", url: ""},
  {id: 7, data: "Conjunto", url: ""},
  {id: 8, data: "Conjunto", url: ""}
];

export function DatasetTable({ isOpen, onClose }) {
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

        <h1 className={styles.datasetTitle}>
          CONJUNTOS DE <span>DADOS UTILIZADOS</span>
        </h1>

        <table className={styles.datasetTable}>
          <thead className={styles.datasetHeader}>
              <th className={styles.th}>CONJUNTO</th>
              <th className={styles.th}>LINK</th>
          </thead>

          {datasets.map((item) => (
            <tr className={styles.datasetRow}>
              <td>{item.data}</td>
              <td>
                <ScaffoldButton
                  value = {"Detalhes"}
                  action = {() => window.open(item.url, '_blank')}
                  orange = {false}
                />
              </td>
            </tr>
          ))}
        </table>
      </div>
    </div>
  );
}