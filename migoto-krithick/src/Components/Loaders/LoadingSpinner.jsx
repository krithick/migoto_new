import React from "react";
import styles from "./Loader.module.css"; // Import the CSS module

const LoadingSpinner = () => {
  return (
    <div className={styles.spinnerContainer}>
      <div className={styles.spinner}>
        <div className={styles.spinnerCircle}></div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
