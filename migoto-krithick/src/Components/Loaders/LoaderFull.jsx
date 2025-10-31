import React from "react";
import styles from "./Loader.module.css"; // Import CSS module

const LoaderFull = () => {
  return (
    <div className={styles.loaderContainer}>
      <div className={styles.spinner}>
        {/* <div className={styles.spinnerCircle}> </div> */}
      </div>
      {/* <span className={styles.text}>Your data is being processed!</span> */}
    </div>
  );
};

export default LoaderFull;
