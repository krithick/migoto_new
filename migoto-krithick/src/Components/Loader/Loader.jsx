import React from "react";
import styles from "./Loader.module.css";

function Loader() {
  return (
    <div className={styles.loaderContainer}>
      <p className={styles.message}>
       Hold on while AI gets creative
        <span className={styles.dot}>.</span>
        <span className={styles.dot}>.</span>
        <span className={styles.dot}>.</span>
      </p>
    </div>
  );
}

export default Loader;
