import React, { useEffect, useState } from "react";
import styles from "../../Components/PopUps/PersonaEditorPopUp.module.css";
import BackIcon from "../../Icons/BackIcon";
import VoiceCard from "../Card/VoiceCard";
import { usePreviewStore } from "../../store";
import axios from "../../service";

function PersonaEditorPopUp() {
  const { isPreview, setIsPreview } = usePreviewStore();

  // Early return to prevent unnecessary mounting and API calls
  // if (!isPreview?.enable || isPreview.value !== "AvatarPopUp") return null;

  let [selected, setSelected] = useState("CharacterDescription");
  let [data, setData] = useState();
  let [thumbnail_url, setThumbnail_url] = useState();
  let [formData, setFormData] = useState({});
  let [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (isPreview?.msg) {
      setData([]);
      axios
        .get(`/avatars/${isPreview.msg}`)
        .then((res) => {
          // setThumbnail_url('/avatarTest.png')
          setThumbnail_url(res.data.thumbnail_url);
          handlePersonaChar(res.data.persona_id[0]);
        })
        .catch((err) => {
          console.log("err: ", err);
        });
    }
  }, [isPreview?.msg]);

  const handlePersonaChar = (id) => {
    axios
      .get(`/personas/${id}`)
      .then((res) => {
        setData(res.data);
        setFormData(res.data);
      })
      .catch((err) => {
        console.log("err: ", err);
      });
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    const { thumbnail_url, ...updateData } = formData;
    axios
      .put(`/personas/${formData.id}`, updateData)
      .then((res) => {
        setData(res.data);
        setIsEditing(false);
        setIsPreview({enable:false,msg:"",value:"AvatarPopUp"})
      })
      .catch((err) => {
        console.log("err: ", err);
      });
  };

  return (
    <div className={styles.PopUpContainer}>
      <div className={styles.avatarPreviewContainer}>
        <div className={styles.avatarPreviewHeader}>
          <div className={styles.page}>
            <div className={styles.currentPage}>Avatar Persona Details</div>
          </div>

          <div className={styles.page2}>
            <div
              className={styles.CloseIcon}
              onClick={() => {
                setIsPreview({ enable: false, msg: "", value: "AvatarPopUp" });
              }}
            >
              X{" "}
            </div>
          </div>
        </div>

        <div className={styles.avatarPreviewBody}>
          <div className={styles.mainContent}>
          <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Persona Type</span>
                <textarea className={styles.customInput} style={{resize: 'none'}} value={formData?.persona_type || ''} onChange={(e) => handleInputChange('persona_type', e.target.value)} readOnly={!isEditing} />
              </div>
          <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Business or Personal</span>
                <textarea className={styles.customInput} style={{resize: 'none'}} value={formData?.business_or_personal || ''} onChange={(e) => handleInputChange('business_or_personal', e.target.value)} readOnly={!isEditing} />
              </div>
          <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Background Story</span>
                <textarea className={styles.customInput} style={{resize: 'none'}} value={formData?.background_story || ''} onChange={(e) => handleInputChange('background_story', e.target.value)} readOnly={!isEditing} />
              </div>
          <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Persona Details</span>
                <textarea className={styles.customInput} style={{resize: 'none'}} value={formData?.persona_details || ''} onChange={(e) => handleInputChange('persona_details', e.target.value)} readOnly={!isEditing} />
              </div>
          <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Situation</span>
                <textarea className={styles.customInput} style={{resize: 'none'}} value={formData?.situation || ''} onChange={(e) => handleInputChange('situation', e.target.value)} readOnly={!isEditing} />
              </div>
          <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Description</span>
                <textarea className={styles.customInput} style={{resize: 'none'}} value={formData?.description || ''} onChange={(e) => handleInputChange('description', e.target.value)} readOnly={!isEditing} />
              </div>
          <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Goal</span>
                <textarea className={styles.customInput} style={{resize: 'none'}} value={formData?.character_goal || ''} onChange={(e) => handleInputChange('character_goal', e.target.value)} readOnly={!isEditing} />
              </div>

          </div>
          <div className={styles.advContent}>
            <div className={styles.imageSection}>
              <p>Preview</p>
              <div>
                <img src={thumbnail_url} alt="" />
              </div>
            </div>

            <div className={styles.smallInputs}>
              <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Name</span>
                <input className={styles.customInput} readOnly type="text" value={formData?.name || ''} />
              </div>
              <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Gender</span>
                <input className={styles.customInput} readOnly type="text" value={formData?.gender || ''} />
              </div>
              <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Age</span>
                <input className={styles.customInput} type="number" value={formData?.age || ''} onChange={(e) => handleInputChange('age', parseInt(e.target.value))} readOnly={!isEditing} />
              </div>
              <div className={styles.inputWrapper}>
                <span className={styles.inputLabel}>Location</span>
                <input className={styles.customInput} type="text" value={formData?.location || ''} onChange={(e) => handleInputChange('location', e.target.value)} readOnly={!isEditing} />
              </div>
            </div>
          </div>
        </div>

        <div className={styles.avatarPreviewFooter}>
          {!isEditing ? (
            <button className={styles.editBtn} onClick={() => setIsEditing(true)}>Edit</button>
          ) : (
            <>
              <button className={styles.editBtn} onClick={handleSave}>Save</button>
              <button className={styles.editBtn} onClick={() => setIsEditing(false)}>Cancel</button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default PersonaEditorPopUp;
