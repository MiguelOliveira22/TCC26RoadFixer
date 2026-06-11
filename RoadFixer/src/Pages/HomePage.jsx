import Banner from "../components/Banner";
import Stats from "../components/Stats";
import Features from "../components/Features";
import DataCollection from "../components/DataCollection";
import { useEffect, useState } from "react";
import { apiPath } from "../Constants";

async function getReports(){
      const res = await fetch(apiPath+"listadatasets/");
      const data = await res.json();
      const formatted = data.content.map((valor) => ({ id: valor.id, data: valor.data }));
      return formatted
}

export default function HomePage() {
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
    <main style={{ backgroundColor: 'var(--preto)' }}>
      <Banner />
      <Stats />
      <Features />
      <DataCollection headers={["DADO", "LINK"]} reports={reports} title="CONJUNTOS DE DADOS" buttonText={(<span>VER MAIS CONJUNTO DE <span>DADOS UTILIZADOS</span></span>)} />
    </main>
  );
}