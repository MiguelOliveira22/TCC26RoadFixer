// DataSetTable.jsx
import styles from "./DataSetTable.module.css";
import ScaffoldButton from "./Button/ScaffoldButton";

const datasets = [
  "CLIMA",
  "TOPOLOGIA",
  "ESTRUTURA FÍSICA DA PISTA",
  "CONJUNTO",
  "CONJUNTO",
  "CONJUNTO",
  "CONJUNTO",
  "CONJUNTO",
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

          {datasets.map((item, index) => (
            <tr className={styles.datasetRow} key={index}>
              <td>{item}</td>
              <td>
                <ScaffoldButton
                  value = {"Detalhes"}
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