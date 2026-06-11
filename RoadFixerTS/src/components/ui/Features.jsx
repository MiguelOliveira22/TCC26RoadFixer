import styles from "./Features.module.css";
import { apiPath } from "../Constants";
import React, { useEffect, useState } from "react";

export default function Features() {
  const [ cards, setCards ] = useState([
    { title: "Monitoramento", desc: "Câmeras ao vivo e sensores de pista 24h.", action: "" },
    { title: "Alertas", desc: "Notificações de acidentes e bloqueios imediatos.", action: "" },
    { title: "Histórico", desc: "Base de dados completa desde 2020.", action: "" }
  ]);

  useEffect(() => {
    async function loadNetwork() {    
      try {
        var network = await fetch(apiPath + "carddata");

        var data = await network.json();
        console.log(data);

        if (network.ok && data.content.length > 0) {
          setCards(data.content);
        }
      }
      catch {}
    }

    loadNetwork();
  }, [ ]);

  return (
    <section id="foco" className={styles.section}>
      <h2 className={styles.title}>
        NOSSO <span className={styles.highlight}>FOCO</span>
      </h2>
      
      <div className={styles.grid}>
        {cards.map((card, i) => (
          <div key={i} className={styles.card}>
            <h3 className={styles.cardTitle}>{card.title}</h3>
            <p>{card.desc}</p>
            <div className={styles.link}>Ver mais →</div>
          </div>
        ))}
      </div>
    </section>
  );
}