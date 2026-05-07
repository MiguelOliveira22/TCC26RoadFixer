import baseStyles from "./BaseButton.module.css";

export default function BaseButton({ value, action }) {    
    return (
        <div className={baseStyles.button} onClick={action}>
            {value}
        </div>
    );
}