import React, { useEffect, useState } from "react";
import { useLOIData, useUserPopupStore } from "../../store";
import styles from "../AvatarCreation/AvatarCreation.module.css";
import SearchIcon from "../../Icons/SearchIcon";
import CreateCourseIcon from "../../Icons/CreateCourseIcon";
import AvatarCard from "../../Components/ModesComponent/AvatarCard";
import CreateAvatarIcon from "../../Icons/CreateAvatarIcon";
import SelectionCard from "../../Components/Card/SelectionCard";
import PersonaSelection from "./PersonaSelection";
import Voice from "./Voice";
import SceneCanvas from "./SceneCanvas";
import { useNavigate } from "react-router-dom";
import AvatarPreview from "../../Components/AvatarPreview/AvatarPreview";
import AvatarPopUp from "../../Components/PopUps/AvatarPopUp";
import BackIcon from "../../Icons/BackIcon";
import { UpdateTimeline } from "../../Components/Timeline/UpdateTImeLine";
import AvatarViewer from "../AvatarViewer/AvatarViewer";

function AvatarCreation({setEditPage}) {
  const { selectedData, setSelectedData } = useLOIData();
  let [activeCourse, setActiveCourse] = useState("all");
  let [currentPage, setCurrentPage] = useState("avatarSelection");
  // let [activeState, setActiveState] = useState("PersonaSelection");
  let [activeState, setActiveState] = useState("Avatar");
  const { message, setMessage } = useUserPopupStore();
  let flow = localStorage.getItem("flow");
  let [datas, setDatas] = useState([]);
  let [data, setData] = useState(datas);
  let navigate = useNavigate()
  let path = window.location.pathname;


  const handleNavigateBack = () => {
    let path = window.location.pathname;
    if(flow == "CourseManagement & editScenario flow"){ 
      setSelectedData("showScenario",null)
      setEditPage()
    }else if(flow == "Create Avatar flow"){
      const cleanedPath = path?.replace("/createAvatar", "/personaCreation");
      navigate(cleanedPath, { state: { myData: "List Of Modules" } });
            UpdateTimeline(5, {
              status: "warning",
              description: ``
            },setSelectedData);
            UpdateTimeline(6, {
              status: "error",
              description: ``
            },setSelectedData);
    }else{
      const cleanedPath = path?.replace("/createAvatar", "/avatarSelection");
      navigate(cleanedPath, { state: { myData: "createAvatar" } });
                            UpdateTimeline(6, {
                              status: "error",
                              description: ``
                            },setSelectedData);
                            UpdateTimeline(5, {
                              status: "warning",
                              description: `In Progress`
                            },setSelectedData);
    }
  }

  const backFunction = () => {
            if (flow == "CourseManagement & editScenario flow") {
              handleNavigateBack();
            } else if (flow == "Create Avatar flow") {
              navigate("/migoto-cms/dashboard");
              clearAllData()
            } else {
              handleBack();
            }
  }

    const handleBack = () => {
    if (flow != "Create Avatar flow") {
      const cleanedPath = path?.replace("/createAvatar", "/avatarSelection");
      navigate(cleanedPath, { state: { myData: "createAvatar" } });      
    } else {      
      const cleanedPath = path?.replace("createAvatar","avatarSelection");
      navigate(cleanedPath);
    }
  };

  
  return (
    <div className={styles.avatarContainer}>
      <div className={styles.avatarHeader1}>
        <div className={styles.avatarHeaderLeft}>
        <BackIcon onClick={()=>{
                let path = window.location.pathname;
                // const cleanedPath = path?.replace("/createAvatar", "");
                const cleanedPath = -1
                if(flow=="Create Avatar flow" || flow == "CourseManagement & editScenario flow"){
                  handleNavigateBack()
                }else{
                  navigate(cleanedPath);          
                  // navigate(cleanedPath, { state: { myData: "Document Upload" } });          
                }
        }} />
          <p>Avatar Creation</p>
        </div>
        <div className={styles.avatarHeaderRight}>
          {/* <button onClick={()=>{}}>
            Create Avatar
            <CreateAvatarIcon />
          </button> */}
        </div>
      </div>

      {/* <div className={styles.avatarHeader2}>
        <div className={styles.avatarHeaderLeft}>
          <div className={styles.currentContent}>
            <div
              className={`${styles.activeHeader} ${
                currentPage == "CoachSelection" && styles.setActiveHeader
              }`}
            >
              <span> 01 </span> Persona Selection
            </div>{" "}
            {" > "}
            <div
              className={`${
                currentPage == "CoachSelection" && styles.activeHeader
              }`}
            >
              <span> 02 </span> Coach AI Selection
            </div>
          </div>
        </div>
      </div> */}
      {/* -------------------Body--------------- */}
      {/*  sidebar */}
      <div className={styles.OverallContainer}>
      <div className={styles.sideBar}>
        <div
          className={`${styles.unselected} ${
            activeState == "Avatar" ? styles.selected : ""
          }`}
          onClick={() => {
            setActiveState("Avatar")
          }}
        >
          Avatar
        </div>
        <div
          className={`${styles.unselected} ${
            activeState == "Avatarview"? styles.selected : ""
          }`}
          onClick={() => {
            // selectedData["PersonaSelection"]?
            // setActiveState("Avatarview")
            // :setMessage({enable: true, msg: "Kindly Select Persona for creating Avatar",state: false});
          }}
        >
          Avatar Preview
        </div>
      </div>

    <div className={styles.ContainerContent}>
    {activeState == "Avatar" && <SceneCanvas setActiveState={()=>{setActiveState("Avatarview")}}/>}
      {activeState == "Avatarview" && <AvatarViewer backFunction={()=>backFunction()}/>}
    </div>
      </div>
    </div>
  );
}

export default AvatarCreation;
