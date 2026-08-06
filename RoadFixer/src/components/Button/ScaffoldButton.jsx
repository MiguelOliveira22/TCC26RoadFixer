import baseStyles from "./BaseButton.module.css";
import scaffoldStyles from "./ScaffoldButton.module.css";

export default function ScaffoldButton({ value, action, orange = true, small = false }) {
  const classNames = [
    baseStyles.button,
    scaffoldStyles.scaffoldButton,
    orange ? scaffoldStyles.scaffoldButtonOrange : scaffoldStyles.scaffoldButtonWhite,
    small ? scaffoldStyles.small : scaffoldStyles.regular
  ].join(" ");

  return (
    <button className={classNames} onClick={action}>
      {value}
    </button>
  );
}