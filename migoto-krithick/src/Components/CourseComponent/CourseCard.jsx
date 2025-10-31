import React from "react";
import styles from "../CourseComponent/CourseCard.module.css";
import { useLOIData } from "../../store";
import PdfIcon from "../../Icons/PdfIcon";


function CourseCard({ data, currentPage, index }) {
    
  //data is the data of card
  //currentpage is indicator like module,scenario,course,modePdf
  const { selectedData, setSelectedData } = useLOIData(); // data of module,scenario,course

  const handleSelectData = () => {
    //card selection
    if (selectedData[currentPage] == data.id) {
      setSelectedData(currentPage, null);
    } else {
      setSelectedData(currentPage, data.id);
    }
  };

  return (
    <div
      className={`${styles.card} ${
        selectedData[currentPage] === data.id ? styles.activeCard : ""
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
        {
        data.thumbnail_url &&
        data.thumbnail_url !== "string" &&
        data.thumbnail_url !== null ? (
          <img src={data.thumbnail_url} alt="" />
        ) : (
          <img src="/avatarImg.png" alt="" />
        )}

        {/* {currentPage == "DocumentFile" && index == 2 && <img src='/example1.jpg' alt="" />} */}
        {/* pdf for document Mode */}
        {currentPage == "DocumentFile" && <PdfIcon />}

        {/* image overlay content only for course,scenario,module */}
        {currentPage != "DocumentFile" && (
          <div className={styles.details}>
            <div className={styles.title}>
              {currentPage!="showAvatar"&&<p>Title</p>}
              {currentPage=="showAvatar"&&<p>Avatar Name</p>}
              {<div>{currentPage=="showAvatar"?data?.name:data?.title}</div>}
            </div>
            {currentPage=="showAvatar"&&<div className={styles.status}>
              <p>Age</p>
              <div>{data?.age}</div>
            </div>}
          </div>
        )}
        {currentPage != "DocumentFile" && (
          <div className={styles.gradient}></div>
        )}
      </div>
      {currentPage != "DocumentFile" && (
        <div className={styles.contentContainer}>
          <div className={styles.courseCreater}>
            <p>created By</p>
            <div>{data?.creater_role?data?.creater_role:data?.created_by_info?data?.created_by_info?.role : "NA"}</div>
          </div>
          <div className={styles.coursePercentage}></div>
        </div>
      )}
      {currentPage == "DocumentFile" && (
        <div className={styles.contentContainer}>
          <div className={styles.titles}>
            <p>Document Title</p>
            <div>{data.title}</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CourseCard;
