import React, { useEffect, useState } from "react";

import CardData from "./cards/CardData";
import styles from "./Stats.module.css";
import { apiPath } from "../Constants";

export default function Stats() {
  const [ cards, setCards ] = useState([
    { title: "BR 330", desc: "Rodovia em Foco" },
    { title: "Acidentes Registrados", desc: "1.204 milhões" },
    { title: "Tempo de Resposta", desc: "12 min" },
  ]);

  useEffect(() => {
    async function loadNetwork() {
      var network = await fetch(apiPath + "statsdata/");
      
      var data = await network.json();
      if (network.ok && data.content.length > 0) {
        setCards(data.content);
      }
    }

    loadNetwork();
  }, [ ]);

  return (
    <section id="estatisticas" className={styles.container}>
      <div className={styles.grid}>
        {cards.map((item, index) => (
          <CardData label={item.title} value={item.desc} key={index}/>
        ))}
      </div>
    </section>
  );
}