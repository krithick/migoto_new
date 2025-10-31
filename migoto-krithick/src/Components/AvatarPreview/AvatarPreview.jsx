import React, { useEffect, useState } from "react";
import styles from "./AvatarPreview.module.css";
import BackIcon from "../../Icons/BackIcon";
import VoiceCard from "../Card/VoiceCard";
import { usePreviewStore } from "../../store";
import axios from "../../service";
function AvatarPreview() {
  const { isPreview, setIsPreview } = usePreviewStore();
  
  // Early return to prevent unnecessary mounting and API calls
  // if (!isPreview?.enable || isPreview.value !== "AvatarPopUp") return null;

  let [selected, setSelected] = useState("CharacterDescription");
  let [data, setData] = useState();
  let [thumbnail_url, setThumbnail_url] = useState();
  const [alreadyPlaying, setAlreadyPlaying] = useState(null);
  const [currentPlaying, setCurrentPlaying] = useState(null);

  useEffect(() => {
    if (isPreview?.msg) {
      setData([])
      axios
      .get(`/avatars/${isPreview.msg}`)
      .then((res) => {
        // setThumbnail_url('/avatarTest.png')
        setThumbnail_url(res.data.thumbnail_url)
        handlePersonaChar(res.data.persona_id[0])
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
      setData(res.data)
    })
    .catch((err) => {
      console.log("err: ", err);
    });
  }

  return (
    <div className={styles.PopUpContainer}>
      <div className={styles.avatarPreviewContainer}>
        <div className={styles.avatarPreviewHeader}>
          <div className={styles.page}>
            <div className={styles.currentPage}>Avatar Preview</div>
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
          {/*  sidebar */}
          {/* <div className={styles.sideBar}>
            <div
              className={`${styles.unselected} ${
                selected == "CharacterDescription" ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected("CharacterDescription");
              }}
            >
              Character Description
            </div>
             <div
              className={`${styles.unselected} ${
                selected == "AvatarVoice" ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected("AvatarVoice");
              }}
            >
              Avatar Voice
            </div> 
          </div> */}
          <div className={styles.content}>
            {selected == "CharacterDescription" && (
              <div className={styles.inputSection}>
                <div className={styles.firstRow}>
                  <div className={styles.charName}>
                    <label htmlFor="">Character Name</label>
                    <input type="text" value={data?.name || ""} readOnly />
                  </div>
                  <div className={styles.charAge}>
                    <label htmlFor="">Age</label>
                    <input type="text" value={data?.age || ""} readOnly />
                  </div>
                </div>
                <div className={styles.secondRow}>
                  <div className={styles.roleCreatedBy}>
                    <label htmlFor="">Role</label>
                    <input type="text" value={data?.persona_type || ""} readOnly />
                  </div>
                  <div className={styles.createdBy}>
                    <label htmlFor="">Gender</label>
                    <input type="text" value={data?.gender || ""} readOnly />
                  </div>
                </div>
                <div className={styles.thirdRow}>
                <p>Core Description</p>
                  <div className={styles.description}>
                    <div className={styles.box}>
                      <div className={styles.boxes}>
                        <div>Personality</div>
                        <p>{data?.persona_details || ""}</p>
                      </div>
                      <div className={styles.boxes}>
                        <div>Background</div>
                        <p>{data?.background_story || ""}</p>
                      </div>
                      <div className={styles.boxes}>
                        <div>Goal</div>
                        <p>{data?.character_goal || ""}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            {/* ---------------------------------------------------voice---------------------------------------- */}
            {selected == "AvatarVoice" && (
              <div className={styles.voiceBody}>
                {data?.map((item, index) => {
                  return (
                    <VoiceCard
                      data={item}
                      key={index}
                      currentPage={"AvatarVoice"}
                      alreadyPlaying={alreadyPlaying}
                      setAlreadyPlaying={setAlreadyPlaying}
                      currentPlaying={currentPlaying}
                      setCurrentPlaying={setCurrentPlaying}
                    />
                  );
                })}
              </div>
            )}
            <div className={styles.imageSection}>
              <p>Preview</p>
              <div>
                <img src={thumbnail_url} alt="" />
              </div>
            </div>
          </div>
        </div>

        <div className={styles.avatarPreviewFooter}>
        </div>
      </div>
    </div>
  );
}

export default AvatarPreview;
