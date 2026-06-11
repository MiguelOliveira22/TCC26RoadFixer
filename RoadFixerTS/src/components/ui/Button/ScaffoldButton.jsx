import baseStyles from "./BaseButton.module.css";
import scaffoldStyles from "./ScaffoldButton.module.css";

export default function ScaffoldButton({ value, action, orange = true, small = false }) {
    return (
        <div className={[
                baseStyles.button,
                scaffoldStyles.scaffoldButton,
                orange ? scaffoldStyles.scaffoldButtonOrange : scaffoldStyles.scaffoldButtonWhite
            ].join(" ")} onClick={action} style={small ? { fontSize: "1rem", width: "fit-content" } : {}}
        >
            {value}
        </div>
    );
}