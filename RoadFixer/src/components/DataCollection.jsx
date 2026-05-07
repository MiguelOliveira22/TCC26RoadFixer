import styles from "./DataCollection.module.css";
import ScaffoldButton from "./Button/ScaffoldButton";
import { DatasetTable } from "../components/DataSetTable";
import { useState } from "react";

export default function DataCollection({ headers, reports, idCabecalho }) {
  const cabecalhos = [
    (<span>CONJUNTO DE <span className={styles.highlight}>DADOS UTILIZADOS</span></span>),
    (<span>HISTÓRICO DE <span className={styles.highlight}>ACIDENTES</span></span>)
  ];

  const buttons = [
    "VER MAIS CONJUNTOS DE DADOS",
    "VER MAIS DADOS HISTÓRICOS"
  ];

  const [openPopup, setOpenPopup] = useState(false);  

  return (
    <section id="relatos" className={styles.section}>
      <h2 className={styles.title}>
        {cabecalhos[idCabecalho]}
      </h2>
      
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              {headers.map((tbHeader) => (
                <th className={styles.th}>{tbHeader}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            { reports.map((link) => {
              return (
                <tr key={link.id} className={styles.tr}>
                  { link.data.map((dt) => (
                    <td className={styles.td}>
                      {dt.url != null ? (
                      <ScaffoldButton
                        value="DETALHES"
                        action={dt.url ? () => window.open(dt.url, '_blank') : dt.action}
                        orange={false}
                        small={true}
                      />) : dt}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
        <ScaffoldButton
          value = { buttons[idCabecalho] }
          action= {() => setOpenPopup(true)}
          orange = {false}
        />
        <DatasetTable
          isOpen={openPopup}
          onClose={() => setOpenPopup(false)}
        />
      </div>
    </section>
  );
}