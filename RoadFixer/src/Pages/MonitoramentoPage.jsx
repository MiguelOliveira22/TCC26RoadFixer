import DataCollection from "../components/DataCollection";
import styles from "./MonitoramentoPage.module.css";
import { useEffect, useState } from "react";
import { apiPath } from "../Constants";

async function getReports() {
  const res = await fetch(apiPath + "accidentHistory/");
  const data = await res.json();
  const formatted = data.content.map((valor) => ({
    id: valor.id,
    data: valor.data,
  }));
  return formatted;
}

export default function MonitoramentoPage() {
  const [reports, setReports] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await getReports();
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
        <p className={styles.loadingText}>Carregando central de monitoramento...</p>
      </div>
    );
  }

  return (
    <main className={styles.mainContainer}>
      <section id="mapa" className={styles.section}>
        {/* Cabeçalho Principal */}
        <div className={styles.header}>
          <span className={styles.kicker}>VISÃO OPERACIONAL EM TEMPO REAL</span>
          <h2 className={styles.title}>
            Central de <span className={styles.highlight}>Monitoramento</span>
          </h2>
          <p className={styles.subtitle}>
            Acompanhe a transmissão ao vivo da câmera principal e consulte o histórico recente de ocorrências rodoviárias.
          </p>
        </div>

        {/* Resumo Operacional Rápido (KPIs) */}
        <div className={styles.kpiGrid}>
          <div className={styles.kpiCard}>
            <span className={styles.kpiLabel}>Câmeras Ativas</span>
            <strong className={styles.kpiValue}>01 / 01</strong>
            <span className={styles.kpiStatusGood}>• Transmitindo HD</span>
          </div>

          <div className={styles.kpiCard}>
            <span className={styles.kpiLabel}>Ocorrências Hoje</span>
            <strong className={styles.kpiValue}>{reports.length}</strong>
            <span className={styles.kpiStatusAlert}>• Requer Atenção</span>
          </div>

          <div className={styles.kpiCard}>
            <span className={styles.kpiLabel}>Status da Rodovia</span>
            <strong className={styles.kpiValue}>Tráfego Normal</strong>
            <span className={styles.kpiStatusGood}>• Trecho Cajamar</span>
          </div>
        </div>

        {/* Transmissão da Câmera (Com largura ajustada e sem distorção) */}
        <div className={styles.camerasSection}>
          <div className={styles.sectionTitleRow}>
            <h3 className={styles.sectionTitle}>Transmissão Principal</h3>
            <span className={styles.liveBadge}>
              <span className={styles.liveDot}></span> TRANSMISSÃO AO VIVO
            </span>
          </div>

          <div className={styles.singleVideoWrapper}>
            <div className={styles.cameraHeader}>
              <div className={styles.cameraInfo}>
                <span className={styles.liveDot}></span>
                <div>
                  <h4 className={styles.cameraTitle}>Câmera 01 - Rod. Anhanguera</h4>
                  <span className={styles.cameraLocation}>Trecho Cajamar</span>
                </div>
              </div>
              <span className={styles.kmBadge}>Km 36 + 000m</span>
            </div>

            <div className={styles.iframeWrapper}>
              <iframe
                src="https://srt01.logicahost.com.br/anhanguera/embed.html"
                title="Câmera Anhanguera - Cajamar Km 36"
                className={styles.cameraIframe}
                allowFullScreen
              />
            </div>
          </div>
        </div>

        {/* Tabela de Histórico */}
        <div className={styles.dataCollectionSection}>
          <DataCollection
            headers={["LOCALIZAÇÃO", "STATUS", "GRAVIDADE", "LINK"]}
            reports={reports}
            title="HISTÓRICO DE OCORRÊNCIAS"
            buttonText={<span>VER HISTÓRICO COMPLETO</span>}
          />
        </div>
      </section>
    </main>
  );
}