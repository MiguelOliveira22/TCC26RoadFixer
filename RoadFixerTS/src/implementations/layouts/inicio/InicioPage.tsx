import Banner from "../components/Banner";
import Stats from "../components/Stats";
import Features from "../components/Features";
import DataCollection from "../components/DataCollection";
import type { ComponentType } from "react";

export default function InicioPage() : ComponentType {
  // Não temos url para os tipos de dados que ainda coletaremos
  const reports = [
    { id: 1, data: ["Clima" , {url: ""}]},
    { id: 2, data: ["Topologia" , {url: ""}]},
    { id: 3, data: ["Estrutura física da pista" , {url: ""}]},
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