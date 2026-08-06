import Banner from "../components/Banner";
import Stats from "../components/Stats";
import Features from "../components/Features";
import DataCollection from "../components/DataCollection";
import styles from "./HomePage.module.css";
import { useEffect, useState } from "react";
import { apiPath } from "../Constants";

async function getReports() {
  const res = await fetch(apiPath + "listadatasets/");
  const data = await res.json();
  const formatted = data.content.map((valor) => ({
    id: valor.id,
    data: valor.data,
  }));
  return formatted;
}

export default function HomePage() {
  const [reports, setReports] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        var data = await getReports();
        data.forEach((x) => {
          x.data[1].url = x.data[1].url.replace("$server/", apiPath);
        });
        setReports(data);
      } catch (error) {
        console.error(error);
      }
    };

    loadData();
  }, []);

  if (reports === null) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
        <p className={styles.loadingText}>Carregando informações...</p>
      </div>
    );
  }

  return (
    <main className={styles.mainContainer}>
      <Banner />
      <Stats />
      <Features />
      <div className={styles.dataSection}>
        <DataCollection
          headers={["DADO", "LINK"]}
          reports={reports}
          title="CONJUNTOS DE DADOS"
          buttonText={
            <span>
              VER MAIS CONJUNTO DE <span>DADOS UTILIZADOS</span>
            </span>
          }
        />
      </div>
    </main>
  );
}