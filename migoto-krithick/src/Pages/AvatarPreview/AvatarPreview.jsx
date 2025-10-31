import React, { useState } from "react";
import styles from "../AvatarPreview/AvatarPreview.module.css";
import BackIcon from "../../Icons/BackIcon";
import CreateAvatar from "../../Icons/CreateAvatar";
import VoiceCard from "../../Components/Card/VoiceCard";
import { usePreviewStore } from "../../store";
import { useNavigate } from "react-router-dom";
import { setSessionStorage } from "../../sessionHelper";
function AvatarPreview() {
  let [selected, setSelected] = useState("CharacterDescription");
          let [datas, setDatas] = useState([
        {
          title: "Micro - aggression",
          percentage: 25,
          id: "qwertyuiop9",
          imageUrl: "/sample.wav",
          description:"Indian Female - Relaxed & Confident",
          status: "In progress",
          createdBy: "Super Admin",
          createdById: "12345",
        },
        {
          title: "Onboarding",
          percentage: 75,
          id: "qwertyuiop10",
          imageUrl: "/sample.wav",
          description:"Indian Female - Relaxed & Confident",
          status: "Yet to assign",
          createdBy: "Admin",
          createdById: "12348",
        },
        {
          title: "Diverse Ethnicity",
          percentage: 100,
          id: "qwertyuiop11",
          imageUrl: "/sample.wav",
          description:"Indian Female - Relaxed & Confident",
          status: "Completed",
          createdBy: "Predefined",
          createdById: "12345",
        },
      ]);
  let [data, setData] = useState(datas);
      const [alreadyPlaying, setAlreadyPlaying] = useState(null);
      const [currentPlaying, setCurrentPlaying] = useState(null);
  const {isPreview, setIsPreview} = usePreviewStore();
 let navigate= useNavigate();
      
  return (
    <div className={styles.avatarPreviewContainer}>
      <div className={styles.CloseIcon} onClick={()=>{setIsPreview({enable:false,msg:[],value:"AvatarPopUp"})}}>X</div>
      <div className={styles.avatarPreviewHeader}>
        <div className={styles.page}>
          <div className={styles.currentPage}>Avatar Preview</div>
        </div>

        <div className={styles.page2}>
          {" "}
          <button onClick={()=>{navigate("createAvatar"),setSessionStorage("personaLimit",0),setIsPreview({enable:false,msg:[],value:"AvatarPopUp"})}}>
            Create Avatar <CreateAvatar />
          </button>
        </div>
      </div>

      <div className={styles.avatarPreviewBody}>

        {/*  sidebar */}
        <div className={styles.sideBar}>
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
        </div>
        <div className={styles.content}>
          {selected == "CharacterDescription" && <div className={styles.inputSection}>
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
                            <p>Empathetic, approachable, and diplomatic. Parsley is known for her active listening skills and is always willing to offer advice or support to employees. She values fairness and strives to create an environment where everyone feels heard and respected.</p>
                        </div>
                        <div className={styles.boxes}>
                            <div>Background</div>
                            <p>Empathetic, approachable, and diplomatic. Parsley is known for her active listening skills and is always willing to offer advice or support to employees. She values fairness and strives to create an environment where everyone feels heard and respected.</p>
                        </div>
                        <div className={styles.boxes}>
                            <div>Goal</div>
                            <p>Empathetic, approachable, and diplomatic. Parsley is known for her active listening skills and is always willing to offer advice or support to employees. She values fairness and strives to create an environment where everyone feels heard and respected.</p>
                        </div>
                    </div>
                </div>
            </div>
          </div>}
          {/* ---------------------------------------------------voice---------------------------------------- */}
          {selected == "AvatarVoice" &&<div className={styles.voiceBody}>
          {data.map((item, index) => {
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
        </div>}
          <div className={styles.imageSection}>
            <p>Preview</p>
            <div>
                <img src="/example2.png" alt="" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AvatarPreview;
