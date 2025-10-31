import React, { useEffect, useState } from "react";
import styles from "../Card/Card.module.css";
import { useLOIData } from "../../store";
import PdfIcon from "../../Icons/PdfIcon";
import { setSessionStorage } from "../../sessionHelper";


function  Card({ data, currentPage, index }) {
  //data is the data of card
  //currentpage is indicator like module,scenario,course,modePdf
  const { selectedData, setSelectedData } = useLOIData(); // data of module,scenario,course
  const [check, setCheck] = useState("id")
  const handleSelectData = () => {
    //card selection

    if(currentPage == "moduleLists"){ // for view users assigned scenario
      if (selectedData[currentPage] == data?.module_id) {
        setSelectedData(currentPage, null);
        setSelectedData("moduleHeader", null);
      } else {
        setSelectedData(currentPage, data?.module_id);
        setSelectedData("moduleHeader", data);
      }
    }
    else if(currentPage == "sessions"){
      if (selectedData[currentPage] == data.scenario_id) {
        setSelectedData(currentPage, null);
        setSelectedData("scenarioHeader", null);
      } else {
        setSelectedData(currentPage, data.scenario_id);
        setSelectedData("scenarioHeader", data);

      }
    }
    else{
      if (selectedData[currentPage] == data.id) {
        setSelectedData(currentPage, null);
      } else {
        setSelectedData(currentPage, data.id);
      }  
    }
    if(currentPage=="List Of Scenario"){
      setSelectedData("template_id",data?.template_id)
      setSessionStorage("template_id",data?.template_id)
      setSessionStorage("LearnModeAvatarInteractionId",data?.learn_mode?.avatar_interaction)
      setSessionStorage("TryModeAvatarInteractionId",data?.try_mode?.avatar_interaction)
      setSessionStorage("AssessModeAvatarInteractionId",data?.assess_mode?.avatar_interaction)
    }
    if(currentPage=="assignedCourse"){
        setSelectedData("courseHeader", data);
    }
  };

  useEffect(() => {
    if(currentPage == "moduleLists"){ // for view users assigned scenario
      setCheck("module_id")
    }
    else if(currentPage == "sessions"){
      setCheck("scenario_id")
    }
  }, [])
  

  return (
    <div
      className={`${styles.card} ${
        selectedData[currentPage] === data[check] ? styles.activeCard : ""
      }`}
      onClick={() => {
        handleSelectData()
      }}
    >
      <div
        className={`${styles.imgContainer} ${
          currentPage == "DocumentFile"
            ? styles.PdfContainer
            : styles.videoContainer
        }`}
      >
        {/* image for course,scenario,module */}
        {/* {currentPage != "DocumentFile" && <img src={data?.thumbnail_url} alt="" />} */}
        {(currentPage != "DocumentFile" && currentPage != "moduleLists" && currentPage != "sessions")&&<img src={data?.thumbnail_url?data.thumbnail_url:"/avatarImg.png"} alt="" />}
        {(currentPage == "moduleLists"||currentPage == "sessions")&&<img src={data?.info?.thumbnail_url?data?.info?.thumbnail_url:"/avatarImg.png"} alt="" />}

        {/* {currentPage == "DocumentFile" && index == 2 && <img src='/example1.jpg' alt="" />} */}
        {/* pdf for document Mode */}
        {currentPage == "DocumentFile" && <PdfIcon />}

        {/* image overlay content only for course,scenario,module */}
        {currentPage != "DocumentFile" && (
          <div className={styles.details}>
            <div className={styles.title}>
              <p>Title</p>
              {(currentPage != "moduleLists"&&currentPage != "sessions")&&<div>{data.title?.length > 30 ? data.title?.slice(0, 30)?.replaceAll(/[_-]/g, " ") + "..." : data?.title?.replaceAll(/[_-]/g, " ")}</div>}
              {(currentPage=="moduleLists"||currentPage == "sessions")&&<div>{data?.info?.title?.length > 30 ? data?.info?.title?.slice(0, 30)?.replaceAll(/[_-]/g, " ") + "..." : data?.info?.title?.replaceAll(/[_-]/g, " ")}</div>}
              {/* {currentPage=="moduleLists"&&<div>{data?.module_info?.title?.length > 30 ? data.title?.slice(0, 30)?.replaceAll(/[_-]/g, " ") + "..." : data?.title?.replaceAll(/[_-]/g, " ")}</div>} */}
            </div>
            <div className={styles.status}>
              {/* <p>Status</p> */}
              {/* <div
                className={
                  data.status == "Yet to assign"
                    ? styles.white
                    : data.status == "In progress"
                    ? styles.yellow
                    : styles.green
                }
              >
                <span className={styles.dot}>·</span>
                <p>{data.is_published}</p>
              </div> */}
            </div>
          </div>
        )}
        {currentPage != "DocumentFile" && (
          <div className={styles.gradient}></div>
        )}
      </div>
      {currentPage != "DocumentFile" && (
        <div className={styles.contentContainer}>
          {<div className={styles.courseCreater}>
            <p>Description</p>
            {(currentPage != "moduleLists"&&currentPage != "sessions")&&<div title={data?.description}>{data?.description?.length > 25 ? data?.description?.slice(0, 25)?.replaceAll(/[_-]/g, " ") + "..." : data.description?.replaceAll(/[_-]/g, " ")}</div>}
            {(currentPage=="moduleLists"||currentPage=="sessions")&&<div title={data?.info?.description}>{data?.info?.description?.length > 25 ? data?.info?.description?.slice(0, 25)?.replaceAll(/[_-]/g, " ") + "..." : data?.info?.description?.replaceAll(/[_-]/g, " ")}</div>}
          </div>}
          <div className={styles.coursePercentage}></div>
        </div>
      )}
      {currentPage == "DocumentFile" && (
        <div className={styles.contentContainer}>
          <div className={styles.titles}>
            <p >Document Title</p>
            <div title={data.title?.replaceAll(/[_-]/g, " ")}>{data.title?.length > 30 ? data?.title?.slice(0, 30)?.replaceAll(/[_-]/g, " ") + "..." : data.title?.replaceAll(/[_-]/g, " ")}</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Card;
