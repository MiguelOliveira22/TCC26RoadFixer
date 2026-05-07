import baseStyles from "./BaseButton.module.css";
import filledStyles from "./FilledButton.module.css";

export default function FilledButton({ value, action }) {    
    return (
        <div className={[baseStyles.button, filledStyles.filledButton].join(" ")} onClick={action}>
            {value}
        </div>
    );
}