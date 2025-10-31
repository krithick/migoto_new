

import React, { useEffect, useState } from "react";
import styles from "../PopUps/OkCancelPopUp.module.css"
import { useLOIData, usePreviewStore } from "../../store";
import { Radio } from "antd";


export default function PersonaPromptPopUp() {
    const { isPreview, setIsPreview } = usePreviewStore();
    const { selectedData, setSelectedData } = useLOIData();
  

    const [gender, setGender] = useState("male"); // "Male" | "Female"
    const [promptText, setPromptText] = useState(""); // textarea input

    useEffect(() => {
        if (isPreview.enable && isPreview.value === "PersonaPrompt") {
            setGender("male");
            setPromptText("");
        }
    }, [isPreview.enable, isPreview.value]);
  
    const handleCancel = () => {
      if (isPreview.resolve) isPreview.resolve(false);
      setIsPreview({ enable: false, msg: "", value: "", resolve: null });
    };

    const handleProceed = () => {
      if (isPreview.resolve) isPreview.resolve({gender:gender,promptText:promptText});
      setIsPreview({ enable: false, msg: "", value: "", resolve: null });
    };

    if (isPreview.enable==false || isPreview.value !== "PersonaPrompt") return null;

    return (
      <div className={styles.popBg}>
        <div className={styles.popupContainer}>
          <div className={styles.promptcontent}>
            <p>Persona Prompt</p>
            <div className={styles.gender}>
            <Radio.Group
              onChange={(e) => setGender(e.target.value)}
              value={gender}
            >
              <Radio value="male">Male</Radio>
              <Radio value="female">Female</Radio>
            </Radio.Group>
            </div>
            <div className={styles.prompt}>
                <textarea 
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                placeholder="Type your prompt here..."></textarea>
            </div>
          </div>
          <div className={styles.btnBox}>
            <div className={styles.cancelBtn} onClick={handleCancel}>Cancel</div>
            <div className={styles.saveBtn} onClick={handleProceed}>Proceed</div>
          </div>
        </div>
      </div>
    );
  }
  