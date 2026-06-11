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
                src="https://srt01.logicahost.com.br/anhanguera/embed.html"
                title="Câmeras Anhanguera 1"
                className={styles.cameraIframe}
                allowFullScreen
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
                src="https://srt01.logicahost.com.br/anhanguera/embed.html" // Substitua pelo link da câmera 2 se houver um diferente
                title="Câmeras Anhanguera 2"
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