import styles from "./CardData.module.css"

export default function CardData({ label, value, index }) {
    return (
        <div className={styles.card} key={index}>
            <div className={styles.accent}></div>
            <div className={styles.sizebox}>
                <h3 className={styles.label}>{label}</h3>
            </div>
            <p className={styles.value}>{value}</p>
        </div>
    );
}