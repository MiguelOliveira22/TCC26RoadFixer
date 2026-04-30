import styles from "./FilledButton.module.css";

export default function FilledButton({ value, action }) {
    return (
        <div className={styles.button} onClick={action}>
          {value}
        </div>
    );
}