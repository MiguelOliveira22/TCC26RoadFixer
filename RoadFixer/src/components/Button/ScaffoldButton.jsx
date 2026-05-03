import styles from "./ScaffoldButton.module.css";

export default function ScaffoldButton({ value, action, orange = true }) {
    return (
        <div className={orange ? styles.buttonOrange : styles.buttonWhite} onClick={action}>
          {value}
        </div>
    );
}