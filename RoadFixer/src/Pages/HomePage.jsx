import Banner from "../components/Banner";
import Stats from "../components/Stats";
import Features from "../components/Features";
import DataCollection from "../components/DataCollection";

export default function HomePage() {
  // Não temos url para os tipos de dados que ainda coletaremos (solução temporaria)
  const reports = [
    { id: 1, data: ["Clima e Condições Meteorológicas" , {url: "https://portal.inmet.gov.br/"}]},
    { id: 2, data: ["Topologia e Georreferenciamento de Rodovias" , {url: "https://dados.gov.br/dados/conjuntos-dados/sistema-nacional-de-viacao-snv"}]},
    { id: 3, data: ["Estrutura Física e Condição de Pistas" , {url: "https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/pesquisa-de-rodovias"}]},
  ];

  return (
    <main style={{ backgroundColor: 'var(--preto)' }}>
      <Banner />
      <Stats />
      <Features />
      <DataCollection headers={["DADO", "LINK"]} reports={reports} idCabecalho={0} />
    </main>
  );
}