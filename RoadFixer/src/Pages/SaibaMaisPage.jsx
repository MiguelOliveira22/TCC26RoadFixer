import React, { useState } from 'react';

export default function SaibaMaisPage() {
  const [secaoAtiva, setSecaoAtiva] = useState('INTRODUÇÃO');

  const conteudos = {
    'INTRODUÇÃO': (
      <>
        <p style={styles.paragraph}>
          Atualmente, mesmo com o constante crescimento da qualidade das rodovias paulistas, em especial a Anhanguera (SP 330), ainda são recorrentes as fatalidades resultantes de acidentes, as dificuldades no acesso posterior das pistas e o consumo de recursos públicos e emergenciais em resposta a aqueles e outros eventos similares.
        </p>
        <p style={styles.paragraph}>
          De acordo com os dados coletados pela ARTESP, no período de um ano, cerca de 2200 acidentes individuais ocorreram na rodovia Anhanguera (SP 330), a qual, de acordo com a CNT, é, simultaneamente, avaliada como a 25ª melhor rodovia, federal ou estadual, no país.
        </p>
        <p style={styles.paragraph}>
          De acordo com esses dados, o objetivo desse projeto é usar um modelo probabilístico capaz de determinar o risco e possibilidade de ocorrência de acidentes nestas pistas e propor, de forma autônoma, soluções preventivas que possam diminuir esse risco, como o posicionamento de radares, sinalização e iluminação.
        </p>
        <p style={styles.paragraph}>
          Nessa lógica, é possível promover diversas melhorias aos motoristas que atuam nessa região, além de possibilitar a melhor alocação de recursos públicos, garantindo melhor eficiência na manutenção e nas condições de tráfego.
        </p>
      </>
    ),
    'METODOLOGIAS': (
    <>
        <p style={styles.paragraph}>Texto sobre as metodologias do RoadFixer...</p>
    </>
    ),
    'SEÇÃO 3': (
    <>
        <p style={styles.paragraph}>Texto sobre as metodologias do RoadFixer...</p>
    </>
    ),
    'REFERÊNCIAS': (
    <>
        <p style={styles.paragraph}>Texto sobre as metodologias do RoadFixer...</p>
    </>
    )
  };

  return (
    <div style={styles.page}>
      <aside style={styles.sidebar}>
        <h2 style={styles.sidebarTitle}>SAIBA MAIS SOBRE O <br/> ROAD<span style={{color: 'var(--laranja)'}}>FIXER</span></h2>
        
        <div style={styles.menu}>
          {Object.keys(conteudos).map((nome) => (
            <button 
              key={nome}
              onClick={() => setSecaoAtiva(nome)}
              style={{
                ...styles.menuButton,
                color: secaoAtiva === nome ? 'var(--laranja)' : '#888'
              }}
            >
              {nome}
            </button>
          ))}
        </div>
      </aside>

      <main style={styles.content}>
        <h2 style={styles.contentTitle}>{secaoAtiva}</h2>
        {conteudos[secaoAtiva]}
      </main>
    </div>
  );
}

const styles = {
  page: {
    display: 'flex',
    minHeight: '100vh',
    backgroundColor: '#0a0a0a',
    color: 'white',
    padding: '80px 5% 0'
  },
  sidebar: {
    width: '30%',
    paddingRight: '50px'
  },
  sidebarTitle: { fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '40px' },
  menu: { display: 'flex', flexDirection: 'column', gap: '15px' },
  menuButton: {
    background: 'none',
    border: 'none',
    textAlign: 'left',
    fontSize: '1.1rem',
    fontWeight: 'bold',
    cursor: 'pointer',
    padding: 0,
    transition: '0.3s'
  },
  content: {
    width: '70%',
    borderLeft: '1px solid #222',
    paddingLeft: '50px'
  },
  contentTitle: { 
    color: 'var(--laranja)', 
    fontSize: '2rem', 
    marginBottom: '30px',
    textTransform: 'uppercase'
  },
  paragraph: {
    fontSize: '1.1rem',
    lineHeight: '1.6',
    marginBottom: '20px',
    color: '#eee'
  }
};