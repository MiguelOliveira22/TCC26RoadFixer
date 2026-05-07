import baseStyles from "./BaseButton.module.css";
import scaffoldStyles from "./ScaffoldButton.module.css";

export default function ScaffoldButton({ value, action, orange = true }) {
    return (
        <div className={[
                baseStyles.button,
                scaffoldStyles.scaffoldButton,
                orange ? scaffoldStyles.scaffoldButtonOrange : scaffoldStyles.scaffoldButtonWhite
            ].join(" ")} onClick={action}
        >
            {value}
        </div>
    );
}