import styles from "./Features.module.css";
import { apiPath } from "../Constants";
import React, { useEffect, useState } from "react";

export default function Features() {
  const [ cards, setCards ] = useState([
    { title: "Monitoramento", desc: "Câmeras ao vivo e sensores de pista 24h." },
    { title: "Alertas", desc: "Notificações de acidentes e bloqueios imediatos." },
    { title: "Histórico", desc: "Base de dados completa desde 2020." }
  ]);
  const [ mounted, setMounted ] = useState(false);

  useEffect(() => {
    async function loadNetwork() {
      try {
        var network = await fetch(apiPath + "");

        if (network.ok && network.json().cards.length > 0 && mounted) {
          setCards(network.json().cards);
        }
      }
      catch {}
    }

    loadNetwork();
    return () => { setMounted(true); };
  });

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