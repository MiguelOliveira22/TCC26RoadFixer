import CardData from "./cards/CardData";
import styles from "./Stats.module.css";

export default function Stats() {
  const data = [
    { label: "BR 330", value: "Rodovia em Foco" },
    { label: "Acidentes Registrados", value: "1.204 milhões" },
    { label: "Tempo de Resposta", value: "12 min" },
  ];

  return (
    <section id="estatisticas" className={styles.container}>
      <div className={styles.grid}>
        {data.map((item, index) => (
          <CardData label={item.label} value={item.value} key={index}/>
        ))}
      </div>
    </section>
  );
}