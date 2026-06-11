import styles from "./DataCollection.module.css";
import ScaffoldButton from "./Button/ScaffoldButton";
import { DatasetTable } from "../components/DataSetTable";
import { useState } from "react";

export default function DataCollection({ headers, reports, title, buttonText }) {
  const [openPopup, setOpenPopup] = useState(false);  

  return (
    <section id="relatos" className={styles.section}>
      <h2 className={styles.title}>
        {title}
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
          value = { buttonText }
          action= {() => setOpenPopup(true)}
          orange = {false}
        />
        <DatasetTable
          isOpen={openPopup}
          onClose={() => setOpenPopup(false)}
          headers={headers}
          title={title}
          datasets={reports}
        />
      </div>
    </section>
  );
}