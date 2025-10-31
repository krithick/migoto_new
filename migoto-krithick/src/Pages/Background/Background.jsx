import React from "react";
import styles from "./Background.module.css";
function Background() {
  return (
    <>
      <div className={styles.background}>
        <div className={styles.pinkContainer}>
          <div className={styles.pink}></div>
        </div>
        <div className={styles.pinkContainer2}>
          <div className={styles.pink}></div>
        </div>
        <div className={styles.blueContainer}>
          <div className={styles.blue}></div>
        </div>
        <div className={styles.blueContainer2}>
          <div className={styles.blue}></div>
        </div>
      </div>
    </>
  );
}

export default Background;
