import Banner from "../components/Banner";
import Stats from "../components/Stats";
import Features from "../components/Features";
import RecentAccidents from "../components/DataCollection";
import ScaffoldButton from "../components/Button/ScaffoldButton";
import { DatasetTable } from "../components/DataSetTable";
import { useState } from "react";

export default function HomePage() {
  const [openPopup, setOpenPopup] = useState(false);  
  return (
    <main style={{ backgroundColor: 'var(--preto)' }}>
      <Banner />
      <Stats />
      <Features />
      <RecentAccidents />
       <ScaffoldButton
        value = {"Ver mais conjuntos de dados"}
        action= {() => setOpenPopup(true)}
        orange = {false}
      />
      <DatasetTable
        isOpen={openPopup}
        onClose={() => setOpenPopup(false)}
      />
    </main>
  );
}