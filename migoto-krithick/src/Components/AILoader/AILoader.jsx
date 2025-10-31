import React from "react";
import styles from "./AILoader.module.css";
import { useLoaderStore } from "../../store";

function AILoader() {
  // let {loading} = useLoaderStore()

  // if(!loading)return
  return (
    <div className={styles.loaderContainer}>
      <div className={styles.message}>
        <div className={styles.LetterContainer}>
            <div className={styles.letter}>L</div>
            <div className={styles.letter}>O</div>
            <div className={styles.letter}>A</div>
            <div className={styles.letter}>D</div>
            <div className={styles.letter}>I</div>
            <div className={styles.letter}>N</div>
            <div className={styles.letter}>G</div>
        </div>
      </div>
      <div className={styles.dotContainer}>
            {[0,1,2].map((i)=>
                (<div key={i} className={styles.dot} style={{ animationDelay: `${i + 0.8}s` }}></div>)
            )}
        </div>
    </div>
  );
}

export default AILoader;