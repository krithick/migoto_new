import React from "react";
import styles from '../PopUps/AvatarPopUp.module.css'

function AvatarPopUp({activeState , setActiveState}) {
  return (
    <div className={styles.PopUpContainer}>
        <div className={styles.header}>
            <div>Avatar Preview</div>
            {activeState!=="PersonaPreview"&&<div> X </div>}
        </div>
      <div className={styles.content}>
          <div className={styles.inputSection}>
            <div className={styles.firstRow}>
              <div className={styles.charName}>
                <label htmlFor="">Character Name</label>
                <input type="text" readOnly />
              </div>
              <div className={styles.charAge}>
                <label htmlFor="">Age</label>
                <input type="text" readOnly />
              </div>
            </div>
            <div className={styles.secondRow}>
              <div className={styles.roleCreatedBy}>
                <label htmlFor="">Role</label>
                <input type="text" readOnly />
              </div>
              <div className={styles.createdBy}>
                <label htmlFor="">Created by</label>
                <input type="text" readOnly />
              </div>
            </div>
            <div className={styles.thirdRow}>
              <div className={styles.description}>
                <p>Core Description</p>
                <div className={styles.box}>
                  <div className={styles.boxes}>
                    <div>Personality</div>
                    <p>
                      Empathetic, approachable, and diplomatic. Parsley is known
                      for her active listening skills and is always willing to
                      offer advice or support to employees. She values fairness
                      and strives to create an environment where everyone feels
                      heard and respected.
                    </p>
                  </div>
                  <div className={styles.boxes}>
                    <div>Background</div>
                    <p>
                      Empathetic, approachable, and diplomatic. Parsley is known
                      for her active listening skills and is always willing to
                      offer advice or support to employees. She values fairness
                      and strives to create an environment where everyone feels
                      heard and respected.
                    </p>
                  </div>
                  <div className={styles.boxes}>
                    <div>Goal</div>
                    <p>
                      Empathetic, approachable, and diplomatic. Parsley is known
                      for her active listening skills and is always willing to
                      offer advice or support to employees. She values fairness
                      and strives to create an environment where everyone feels
                      heard and respected.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        <div className={styles.imageSection}>
          <p>Preview</p>
          <div>
            <img src="/example2.png" alt="" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default AvatarPopUp;
