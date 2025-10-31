import React from "react";
import styles from "../Card/SelectionCard.module.css";
import { useLOIData, usePreviewStore } from "../../store";
import PdfIcon from "../../Icons/PdfIcon";
import PreviewIcon from "../../Icons/PreviewIcon";
import PlusIcon from "../../Icons/PlusIcon";
import TickIcon from "../../Icons/TickIcon";
import CheckIcon from "../../Icons/CheckIcon";

function SelectionCard({ data, currentPage, index }) {
  const { selectedData, setSelectedData } = useLOIData();
  const {isPreview, setIsPreview} = usePreviewStore();

  const handleSelectData = () => {
    //card selection
    const currentData = selectedData[currentPage] || [];

    let updatedData;

    if (currentData?.includes(data.id)) {
      // Remove item
      updatedData = currentData.filter((id) => id !== data.id);
    } else {
      // Add item
      updatedData = [...currentData, data.id];
    }

    setSelectedData(currentPage, updatedData);
  };
 
  return (
    
    <div
      className={`${styles.card}`}
      onClick={() => {
        handleSelectData(data);
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
        
        {
  (data.thumbnail_url && data.thumbnail_url !== "string" && data.thumbnail_url !== null)
    ? <img src={data.thumbnail_url} alt="" />
    : <img src="/avatarImg.png" alt="" />
}
        {/* { (data.thumbnail_url &&  data.thumbnail_url !== "string") ? <img src={data.thumbnail_url} alt="" /> : <img src={"/avatarImg.png"} alt="" />} */}

        {/* image overlay content only for course,scenario,module */}
        {<div className={styles.details}> 
          <div className={styles.title}>
            <p>Title</p>
            <div>{data?.name?data?.name:data?.title}</div>
          </div>
          <div className={styles.status}>
            {/* <p>Status</p>
            <div
              className={
                data.status == "Yet to assign"
                  ? styles.white
                  : data.status == "In progress"
                  ? styles.yellow
                  : styles.green
              }
            ><span className={styles.dot}>Â·</span>
              <p>{data.status}</p>
            </div> */}
          </div>
        </div>}
        <div
            className={styles.previewIcon}
            onClick={() => {
              setIsPreview({enable:true,msg:data.id,value:"AvatarPopUp"})
            }}
          >
            <PreviewIcon />
          </div>
        {/* <PreviewIcon className={styles.previewIcon} onClick={()=>{setIsPreview({enable:true,msg: data,value:"AvatarPopUp"})}} /> */}
        <div className={styles.gradient}></div>
      </div>
      {
        <div className={styles.contentContainer}>
          <div className={styles.courseCreater}>
            <p>created By</p>
            <div>{data.creater_role}</div>
          </div>
          {currentPage == "avatarSelection" && 
            <div
              className={`${
                selectedData[currentPage]?.includes(data.id)
                  ? styles.activeCard
                  : styles.selectedIndicator
              }`}
              // onClick={() => {
              //   handleSelectData(data);
              // }}
        
            >
              {selectedData[currentPage]?.includes(data.id) ? (
                <TickIcon />
              ) : (
                <PlusIcon />
              )}
            </div>
          }
          {currentPage=="CoachSelection" && 
            <div
              className={`${styles.unassigned} ${
                selectedData[currentPage]?.includes(data.id)
                  ? styles.assigned
                  : ''
              }`}
              onClick={() => {
                handleSelectData(data);
              }}
            >
              {!selectedData[currentPage]?.includes(data.id) ? (
                <div>Assign</div>
              ) : (
                <div>
                  <CheckIcon  className={styles.CheckIcon}/>
                  Assigned
                </div>
              )}
            </div>
          }
        </div>
      }
    </div>
  );
}

export default SelectionCard;
