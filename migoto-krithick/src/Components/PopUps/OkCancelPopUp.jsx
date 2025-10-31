import React from "react";
import styles from "../PopUps/OkCancelPopUp.module.css"
import { usePreviewStore } from "../../store";


export default function OkCancelPopUp() {
    const { isPreview, setIsPreview } = usePreviewStore();
  
    if (isPreview.enable==false || isPreview.value !== "ok/cancel") return null;
  
    const handleCancel = () => {
      if (isPreview.resolve) isPreview.resolve(false);
      setIsPreview({ enable: false, msg: "", value: "", resolve: null });
    };

    const handleProceed = () => {
      if (isPreview.resolve) isPreview.resolve(true);
      setIsPreview({ enable: false, msg: "", value: "", resolve: null });
    };

    return (
      <div className={styles.popBg}>
        <div className={styles.popupContainer}>
          <div className={styles.popupHeader}>
          <h4 className={styles.popUpContent1}>Confirmation</h4>
          <p className={styles.content}>{isPreview.msg}</p>
          </div>
          <div className={styles.btnBox}>
            <div className={styles.cancelBtn} onClick={handleCancel}>Cancel</div>
            <div className={styles.saveBtn} onClick={handleProceed}>Proceed</div>
          </div>
        </div>
      </div>
    );
  }
  