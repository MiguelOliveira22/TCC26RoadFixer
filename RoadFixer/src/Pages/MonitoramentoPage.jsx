import DataCollection from "../components/DataCollection";
import styles from "./MonitoramentoPage.module.css";
import { useEffect, useState } from "react";
import { apiPath } from "../Constants";

async function getReports(){
      const res = await fetch(apiPath+"accidentHistory/");
      const data = await res.json();
      const formatted = data.content.map((valor) => ({ id: valor.id, data: valor.data }));
      return formatted
}

export default function MonitoramentoPage() {
  const [reports, setReports] = useState(null)

  useEffect(() => {
          const loadData = async () => {
              try {
                  const data = await getReports();
                  setReports(data);
              } catch (error) {
               console.error(error);
              }
          };
  
          loadData()
      }, []);
  
  if (reports === null) {
    return (
      <div>
        <p>Carregando informações...</p>
      </div>
    );
  }
  return (
    <>
      <section id="mapa" className={styles.section}>
        <div className={styles.header}>
          <p className={styles.kicker}>VISÃO OPERACIONAL</p>
          <h2 className={styles.title}>Câmera</h2>
          <p className={styles.subtitle}>Tela dedicada para consultar os relatos e visualizar as transmissões ao vivo.</p>
        </div>

        {/* CONTAINER DOS DOIS VÍDEOS LADO A LADO */}
        <div className={styles.camerasGrid}>
          
          {/* CÂMERA 1 */}
          <div className={styles.videoWrapper}>
            <div className={styles.cameraHeader}>
              <span className={styles.liveDot}></span>
              <h3 className={styles.cameraTitle}>Transmissão Ao Vivo - Câmera 1</h3>
            </div>
            <div className={styles.iframeWrapper}>
              <iframe
                src="https://srt01.logicahost.com.br/anhanguera/embed.html"
                title="Câmeras Anhanguera 1"
                className={styles.cameraIframe}
                allowFullScreen
              />
            </div>
          </div>
        </div>
      </section>

      <DataCollection headers={["LOCALIZAÇÃO", "STATUS", "GRAVIDADE", "LINK"]} reports={reports} title="HISTÓRICO" buttonText={(<span>VER HISTÓRICO</span>)}></DataCollection>
    </>
  );
}