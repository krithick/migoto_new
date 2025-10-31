import React, { useState } from "react";
import styles from "../EditDocument/AddPrompt.module.css"
import { usePreviewStore } from "../../../../store";

export default function AddPrompt() {
    const { isPreview, setIsPreview } = usePreviewStore();
    const [inputText, setInputText] = useState("");
    const [isError, setIsError] = useState(false);
  
    if (isPreview.enable==false || isPreview.value !== "addPrompt") return null;
  
    const handleCancel = () => {
      if (isPreview.resolve) isPreview.resolve(false);
      setIsPreview({ enable: false, msg: "", value: "", resolve: null });
      setInputText("");
      setIsError(false);
    };

    const handleProceed = () => {
      const trimmedText = inputText.trim();
      if (!trimmedText) {
        setInputText("")
        setIsError(true);
        setTimeout(() => setIsError(false), 1000);
        return;
      }
      if (isPreview.resolve) isPreview.resolve(trimmedText);
      setIsPreview({ enable: false, msg: "", value: "", resolve: null });
      setInputText("");
      setIsError(false);
    };

    return (
      <div className={styles.popBg}>
        <div className={`${styles.popupContainer} ${isError ? styles.red : ""}`}>
          <div className={styles.popupHeader}>
            <h4 className={styles.popUpContent1}>Add New Points to {isPreview?.msg?.replaceAll(/[_-]/g, " ")}</h4>
            <textarea 
              placeholder={isError ? "Enter Valid Data" : `Enter Points to ${isPreview?.msg?.replaceAll(/[_-]/g, " ")}`}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          </div>
          <div className={styles.btnBox}>
            <div className={styles.cancelBtn} onClick={handleCancel}>Cancel</div>
            <div className={styles.saveBtn} onClick={handleProceed}>Proceed</div>
          </div>
        </div>
      </div>
    );
  }
  