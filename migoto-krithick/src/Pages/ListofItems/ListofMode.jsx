import React, { useEffect, useState } from "react";
import styles from "../ListofItems/ListofMode.module.css";
import { useLOIData, useModeData } from "../../store";
import CurrentMode from "./CurrentMode";

function ListofMode({data}) {

  let [arr,setArr] = useState([
    {title:"Learn Mode",description:"Learn Mode allows you to engage with course content at your own pace, offering a focused and interactive experience to master new skills and knowledge.", label:"Click Here to assign Learn Mode",enable:false}
    ,{title:"Try Mode",description:"Try Mode gives you a hands-on learning experience, allowing you to apply concepts in a practical setting and build confidence through real-time practice at your own pace.",label:"Click Here to assign Try Mode",enable:false}
    ,{title:"Assess Mode",description:"Learn Mode allows you to engage with course content at your own pace, offering a focused and interactive experience to master new skills and knowledge.", label:"Click Here to assign Learn Mode",enable:false}
  ]);
  
  let [activeCourse, setActiveCourse] = useState(arr[0]);
  let [currentPage, setCurrentPage] = useState("Select Mode");
  const {isOpen,setIsOpen} = useModeData();

  useEffect(()=>{
    setIsOpen("Learn Mode",true);
    setIsOpen("Learn Mode avatar",true);
    setIsOpen("Assess Mode avatar",true);
    setIsOpen("Assess Mode video",true);
    setIsOpen("Assess Mode pdf",true);
    setIsOpen("Try Mode avatar",true);
    setIsOpen("Try Mode",true);
    setIsOpen("Assess Mode",true);    
  },[])

// console.log(isOpen);

  return (
    <div className={styles.loiContainer}>
      <div className={styles.loiHeader}>
          <div className={styles.totalBox}>
            <div
              className={`${styles.box} ${
                activeCourse.title === "Learn Mode" ? styles.active : ""
              }`}
              onClick={() => {
                setActiveCourse(arr[0])
              }}
            >
              Learn Mode
            </div>
            <div
              className={`${styles.box} ${
                activeCourse.title =="Try Mode" ? styles.active : ""
              }`}
              onClick={() => {
                setActiveCourse(arr[1])
              }}
            >
              Try Mode
            </div>
            <div
              className={`${styles.box} ${
                activeCourse.title =="Assess Mode"? styles.active : ""
              }`}
              onClick={() => {
                setActiveCourse(arr[2])
              }}
            >
              Assess Mode
            </div>
          </div>
      </div>
              {/* -------------------Body--------------- */}
        <CurrentMode activeCourse={activeCourse} data={data}/>
    </div>
  );
}

export default ListofMode;
