import React, { useEffect, useState } from "react";
import { useLOIData, useModeData, usePreviewStore } from "../../store";
import styles from '../AvatarCreation/PersonaSelection.module.css'
import SelectionCard from "../../Components/Card/SelectionCard";
import AvatarCard from "../../Components/ModesComponent/AvatarCard";
import WarningIcon from "../../Icons/WarningIcon";
import DownloadIcon from "../../Icons/DownloadIcon";
import Card from "../../Components/Card/Card";
import axios from '../../service'
import { Navigate, useNavigate } from "react-router-dom";
function PersonaSelection({setActiveState}) {
      let [currentPage, setCurrentPage] = useState("PersonaSelection");
      let flow = localStorage.getItem("flow")
      let [warn, setWarn] = useState(false);
      const {isOpen,setIsOpen} = useModeData();
      const {isPreview, setIsPreview} = usePreviewStore();
      let [datas, setDatas] = useState([]);
      const { selectedData, setSelectedData } = useLOIData();
      let [activeCourse, setActiveCourse] = useState("all");
      let [data, setData] = useState(datas);
      let navigate = useNavigate();

        const handleChangeCourse = (props) => {
          setActiveCourse(props);
      
          if (props == "all") {
            setData(datas);
          } else if (props === "Me") {
            setData(datas.filter((item) => item.createdBy === props));
          }
        };

      const fetchPersona = () => {
        if(!isPreview.enable)
          axios
            .get("/scenario/personas/v2/list")
            .then((res) => {
              setDatas(res.data)
              setData(res.data)
            })
            .catch((err) => {
              console.log("err: ", err);
            });
      }

        useEffect(()=>{
          fetchPersona()
        },[isPreview.enable])
    
  return (
    <>
    <div className={styles.pageHeader}>
    <div className={styles.activePage}>
        <p>Persona Selection</p>
        {/* <div className={styles.out}><span onClick={()=>{setWarn(!warn)}}> ? </span></div>
            {warn && <div className={styles.warning}>
                <div> <WarningIcon /> Instruction :</div>
                <p>Download the Template File and fill it with proper data</p>
                <p>Once you have downloaded and filled the Template file, upload it</p>
                <p>It is important to follow the same format as the Template, wrongly formatted files will not be processed</p>
            </div>} */}
    </div>
    {flow != "CourseManagement & editScenario flow" &&<div className={styles.buttonGroups}>
        <button className={styles.downloadTemplate} onClick={()=>{navigate("personaCreation"),setSelectedData("personaCreated",1)}}>Create Persona</button>
    </div>}
    </div>
      <div className={styles.avatarHeader3}>
        <div className={styles.avatarHeaderLeft}>
          <div className={styles.totalBox}>
            <div
              className={`${styles.box} ${
                activeCourse === "all" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("all");
              }}
            >
              All
            </div>
            <div
              className={`${styles.box} ${
                activeCourse === "Predefined" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("Predefined");
              }}
            >
              Pre - Defined Courses
            </div>
            <div
              className={`${styles.box} ${
                activeCourse === "Super Admin" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("Super Admin");
              }}
            >
              Created by Super Admin
            </div>
            <div
              className={`${styles.box} ${
                activeCourse === "Admin" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("Admin");
              }}
            >
              Created by Admin
            </div>
            <div
              className={`${styles.box} ${
                activeCourse === "Me" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("Me");
              }}
            >
              Created by Me
            </div>
          </div>
        </div>
      </div>
      <div className={styles.loiBodyOuter}>
        <div className={styles.loiBody}>
          {data.map((item, index) => {
            return (
              <AvatarCard
                data={item}
                key={index}
                currentPage={currentPage}
              />
            );
          })}
        </div>
      </div>
    </>
  );
}

export default PersonaSelection;
