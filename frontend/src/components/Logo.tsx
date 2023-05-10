import styles from "./Logo.module.css";

const Logo = () => (
  <div id={styles["logo"]}>
    <h1>
      <span id={styles["logo-small-text"]}>Rhode Island</span>
      <span id={styles["logo-big-text"]}>Open Meetings</span>
    </h1>
  </div>
);

export default Logo;
