import DataCollection from "../components/DataCollection";
import styles from "./MonitoramentoPage.module.css";

export default function MonitoramentoPage() {
  const reports = [
    { id: 1, data: ["Anhanguera KM 36", "Fluxo Normal", "BAIXA", { url: "" }] },
    { id: 2, data: ["BR-330 KM 012", "1 PESSOA", "BAIXA", { url: "" }] },
    { id: 3, data: ["BR-330 KM 167", "3 PESSOAS", "MEDIA", { url: "" }] },
  ];

  return (
    <>
      <section id="mapa" className={styles.section}>
        <div className={styles.header}>
          <p className={styles.kicker}>VISÃO OPERACIONAL</p>
          <h2 className={styles.title}>Câmeras</h2>
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
                src="https://www.rodoviaanhanguera.com.br/cameras-anhanguera.php"
                title="Câmeras Anhanguera 1"
                className={styles.cameraIframe}
                scrolling="no"
                sandbox="allow-scripts allow-same-origin"
              />
            </div>
          </div>

          {/* CÂMERA 2 */}
          <div className={styles.videoWrapper}>
            <div className={styles.cameraHeader}>
              <span className={styles.liveDot}></span>
              <h3 className={styles.cameraTitle}>Transmissão Ao Vivo - Câmera 2</h3>
            </div>
            <div className={styles.iframeWrapper}>
              <iframe
                src="https://www.rodoviaanhanguera.com.br/cameras-anhanguera.php" // Substitua pela URL da segunda câmera se for diferente
                title="Câmeras Anhanguera 2"
                className={styles.cameraIframe}
                scrolling="no"
                sandbox="allow-scripts allow-same-origin"
              />
            </div>
          </div>

        </div>
      </section>

      <DataCollection headers={["LOCALIZAÇÃO", "STATUS", "GRAVIDADE", "LINK"]} reports={reports} idCabecalho={1}></DataCollection>
    </>
  );
}