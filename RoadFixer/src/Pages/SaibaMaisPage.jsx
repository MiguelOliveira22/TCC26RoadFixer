import React, { useState } from 'react';
import styles from "./SaibaMaisPage.module.css";

export default function SaibaMaisPage() {
  const [secaoAtiva, setSecaoAtiva] = useState('INTRODUÇÃO');

  const conteudos = {
    'INTRODUÇÃO': (
      <div className={styles.fadeIn}>
        <p className={styles.paragraph}>
          Atualmente, mesmo com o constante crescimento da qualidade das rodovias paulistas, em especial a Anhanguera (SP-330), ainda são recorrentes as fatalidades resultantes de acidentes, as dificuldades no acesso posterior às pistas e o consumo de recursos públicos e emergenciais em resposta a esses e outros eventos similares.
        </p>
        <p className={styles.paragraph}>
          De acordo com os dados coletados pela ARTESP, no período de um ano, cerca de 2.200 acidentes individuais ocorreram na rodovia Anhanguera (SP-330), a qual, segundo a CNT, é avaliada como a 25ª melhor rodovia, federal ou estadual, do país.
        </p>
        <p className={styles.paragraph}>
          Com base nesses dados, o objetivo deste projeto é utilizar um modelo probabilístico capaz de determinar o risco e a possibilidade de ocorrência de acidentes nestas pistas e propor, de forma autônoma, soluções preventivas que possam diminuir esse risco, como o posicionamento estratégico de radares, sinalização e iluminação.
        </p>
        <p className={styles.paragraph}>
          Nessa lógica, é possível promover diversas melhorias aos motoristas que trafegam nessa região, além de possibilitar uma melhor alocação de recursos públicos, garantindo maior eficiência na manutenção e nas condições de tráfego.
        </p>
      </div>
    ),
    'METODOLOGIAS': (
      <div className={styles.fadeIn}>
        <p className={styles.paragraph}>
          Atualmente, estamos estudando metodologias para a modelagem e interpretação de múltiplos tipos de informação, como temperatura, condições da pista, topologia e outros dados associados, para o desenvolvimento de um modelo de risco.
        </p>
        <p className={styles.paragraph}>
          Considerando os estudos pesquisados, como os de Ihueze e Onwurah (2018) e de Liliana, Mohamed e Tarek (2022), buscamos associar uma abordagem de visualização da rodovia como um conjunto de grafos ao modelo ARIMAX (AutoRegressive Integrated Moving Average with Explanatory Variables). Isso nos permitirá analisar as condições individuais que qualificam a causa do acidente, ao mesmo tempo em que observamos a noção espacial.
        </p>
        <p className={styles.paragraph}>
          Simultaneamente, buscamos desenvolver um modelo autônomo capaz de analisar esses dados e promover soluções e alterações para a porção espacial e de fiscalização (radares) dos problemas encontrados nas pistas, a fim de diminuir a probabilidade de ocorrência de acidentes.
        </p>
        <p className={styles.paragraph}>
          Portanto, com essas soluções implementadas, seremos capazes de desenvolver um sistema de mapas que apresente a taxa de risco para cada aresta da representação gráfica e demonstre onde os elementos devem ser posicionados para mitigar esse tipo de evento.
        </p>
      </div>
    ),
    'REFERÊNCIAS': (
      <div className={`${styles.fadeIn} ${styles.references}`}>
        <p className={styles.paragraph}>
          LILIANA, Q.; MOHAMED, M. W.; TAREK, S. Safety models incorporating graph theory based transit indicators, 2022.
        </p>
        <p className={styles.paragraph}>
          IHUEZE, C. C.; ONWURAH, U. O. Road traffic accidents prediction modelling: An analysis of Anambra State, Nigeria. <em>Accident Analysis & Prevention</em>, v. 112, p. 21-29, 2018.
        </p>
        <p className={styles.paragraph}>
          WENQI, L.; DONGYU, L.; MENGHUA, Y. A model of traffic accident prediction based on convolutional neural network. <em>IEEE Xplore</em>, 2017. Disponível em: <a href='https://ieeexplore.ieee.org/document/8056908/authors#authors' target='_blank' rel='noreferrer' className={styles.highlight}>https://ieeexplore.ieee.org/document/8056908</a>. Acesso em: 16 abr. 2026.
        </p>
        <p className={styles.paragraph}>
          D’AVILA, R. F. Modelo sistêmico para detecção de pontos críticos em rodovias com base em segmentos homogêneos. 2025. Dissertação (Mestrado em Engenharia de Transportes) – Universidade Federal de Minas Gerais, Belo Horizonte, 2025.
        </p>
      </div>
    )
  };

  return (
    <div className={styles.page}>
      <aside className={styles.sidebar}>
        <h2 className={styles.sidebarTitle}>
          SAIBA MAIS SOBRE O <br />
          ROAD<span className={styles.brandHighlight}>FIXER</span>
        </h2>
        
        <nav className={styles.menu}>
          {Object.keys(conteudos).map((nome) => (
            <button 
              key={nome}
              onClick={() => setSecaoAtiva(nome)}
              className={`${styles.menuButton} ${secaoAtiva === nome ? styles.active : ''}`}
            >
              {nome}
            </button>
          ))}
        </nav>
      </aside>

      <main className={styles.content}>
        <h2 className={styles.contentTitle}>{secaoAtiva}</h2>
        {conteudos[secaoAtiva]}
      </main>
    </div>
  );
}