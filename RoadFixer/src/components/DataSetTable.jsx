// DataSetTable.jsx
import styles from "./DataSetTable.module.css";
import ScaffoldButton from "./Button/ScaffoldButton";

const datasets = [
  { 
    id: 1, 
    data: "Clima e Condições Meteorológicas", 
    url: "https://portal.inmet.gov.br/" 
  },
  { 
    id: 2, 
    data: "Topologia e Georreferenciamento de Rodovias", 
    url: "https://dados.gov.br/dados/conjuntos-dados/sistema-nacional-de-viacao-snv" 
  },
  { 
    id: 3, 
    data: "Estrutura Física e Condição de Pistas", 
    url: "https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/pesquisa-de-rodovias" 
  },
  { 
    id: 4, 
    data: "Microdados de Acidentes em Rodovias Federais", 
    url: "https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf" 
  },
  { 
    id: 5, 
    data: "Painel de Acidentes Rodoviários", 
    url: "https://cnt.org.br/painel-acidente" 
  },
  { 
    id: 6, 
    data: "Dados Abertos de Infrações e Tráfego", 
    url: "https://dadosabertos.artesp.sp.gov.br/" 
  },
  { 
    id: 7, 
    data: "Estatísticas de Acidentes e Volume de Tráfego", 
    url: "https://www.der.sp.gov.br/WebSite/Servicos/DadosAbertos.aspx" 
  },
  { 
    id: 8, 
    data: "Dados de Frota de Veículos por Município", 
    url: "https://www.gov.br/senatran/pt-br/assuntos/estatisticas/dados-estatisticas-frota-de-veiculos" 
  }
];

export function DatasetTable({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className={styles.datasetOverlay} onClick={onClose}>
      <div
        className={styles.datasetModal}
        onClick={(e) => e.stopPropagation()}
      >
        <button className={styles.datasetBackBtn} onClick={onClose}>
          ← VOLTAR
        </button>

        <h1 className={styles.datasetTitle}>
          CONJUNTOS DE <span>DADOS UTILIZADOS</span>
        </h1>

        <table className={styles.datasetTable}>
          <thead className={styles.datasetHeader}>
            <tr> {/* Correção importante aqui */}
              <th className={styles.th}>CONJUNTO</th>
              <th className={styles.th}>LINK</th>
            </tr>
          </thead>
          <tbody> {/* Correção estrutural importante aqui */}
            {datasets.map((item) => (
              <tr key={item.id} className={styles.datasetRow}> {/* Adicionado o atributo 'key' */}
                <td>{item.data}</td>
                <td>
                  <ScaffoldButton
                    value={"Detalhes"}
                    action={() => window.open(item.url, '_blank')}
                    orange={false}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}