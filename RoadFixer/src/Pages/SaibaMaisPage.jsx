import React, { useState } from 'react';
import styles from "./SaibaMaisPage.module.css";


export default function SaibaMaisPage() {
  const [secaoAtiva, setSecaoAtiva] = useState('INTRODUÇÃO');

  const conteudos = {
    'INTRODUÇÃO': (
      <>
        <p className={styles.paragraph}>
          Atualmente, mesmo com o constante crescimento da qualidade das rodovias paulistas, em especial a Anhanguera (SP 330), ainda são recorrentes as fatalidades resultantes de acidentes, as dificuldades no acesso posterior das pistas e o consumo de recursos públicos e emergenciais em resposta a aqueles e outros eventos similares.
        </p>
        <p className={styles.paragraph}>
          De acordo com os dados coletados pela ARTESP, no período de um ano, cerca de 2200 acidentes individuais ocorreram na rodovia Anhanguera (SP 330), a qual, de acordo com a CNT, é, simultaneamente, avaliada como a 25ª melhor rodovia, federal ou estadual, no país.
        </p>
        <p className={styles.paragraph}>
          De acordo com esses dados, o objetivo desse projeto é usar um modelo probabilístico capaz de determinar o risco e possibilidade de ocorrência de acidentes nestas pistas e propor, de forma autônoma, soluções preventivas que possam diminuir esse risco, como o posicionamento de radares, sinalização e iluminação.
        </p>
        <p className={styles.paragraph}>
          Nessa lógica, é possível promover diversas melhorias aos motoristas que atuam nessa região, além de possibilitar a melhor alocação de recursos públicos, garantindo melhor eficiência na manutenção e nas condições de tráfego.
        </p>
      </>
    ),
    'METODOLOGIAS': (
    <>
        <p className={styles.paragraph}>Texto sobre as metodologias do RoadFixer...</p>
    </>
    ),
    'SEÇÃO 3': (
    <>
        <p className={styles.paragraph}>Texto sobre as metodologias do RoadFixer...</p>
    </>
    ),
    'REFERÊNCIAS': (
    <>
        <p className={styles.paragraph}>Texto sobre as metodologias do RoadFixer...</p>
    </>
    )
  };

  return (
    <div className={styles.page}>
      <aside className={styles.sidebar}>
        <h2 className={styles.sidebarTitle}>SAIBA MAIS SOBRE O <br/> ROAD<span className={{color: 'var(--laranja)'}}>FIXER</span></h2>
        
        <div className={styles.menu}>
          {Object.keys(conteudos).map((nome) => (
            <button 
              key={nome}
              style = {{color: secaoAtiva === nome ? 'var(--laranja)' : '#888'}}
              onClick={() => {setSecaoAtiva(nome)}}
              className={ styles.menuButton }
            >
              {nome}
            </button>
          ))}
        </div>
      </aside>

      <main className={styles.content}>
        <h2 className={styles.contentTitle}>{secaoAtiva}</h2>
        {conteudos[secaoAtiva]}
      </main>
    </div>
  );
}
