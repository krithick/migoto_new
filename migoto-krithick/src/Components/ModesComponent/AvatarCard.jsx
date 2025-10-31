import React, { useState } from "react";
import styles from "../Card/Card.module.css";
import { useLOIData, useModeData, usePreviewStore } from "../../store";
import PdfIcon from "../../Icons/PdfIcon";
import PreviewIcon from "../../Icons/PreviewIcon";

function AvatarCard({ data, currentPage, index, setActiveState }) {
  console.log('currentPage: ', currentPage);
  //data is the data of card
  //currentpage is indicator like module,scenario,course,modePdf
  const { selectedData, setSelectedData } = useLOIData(); // data of module,scenario,course
  const { isOpen, setIsOpen } = useModeData();
  const { isPreview, setIsPreview } = usePreviewStore();

  const handleSelectData = () => {
    //card selection
    if (selectedData[currentPage] == data.id) {
      setSelectedData(currentPage, null);
    } else {
      setSelectedData(currentPage, data.id);
    }
  };
  // if(uploadDoc==true || uploadDoc==false){
  // let [pdfVideo,setPdfVideo] = useState(uploadDoc?"Doc Upload":"video Upload")
  // }

  const handleMultiSelectData = () => {
    //card selection
    const currentData = selectedData[currentPage] || [];

    let updatedData;

    if (currentData?.includes(data.id)) {
      // Remove item
      updatedData = currentData?.filter((id) => id !== data.id);
    } else {
      // Add item
      updatedData = [...currentData, data.id];
    }
    setSelectedData(currentPage, updatedData);
  };
  return (
    <div
      className={`${
        currentPage == "Course Doc Upload" ? styles.cardModify : styles.card
      } ${
        selectedData[currentPage]?.includes(data.id) ? styles.activeCard : ""
      }`}
      onClick={() => { 
      
        currentPage == "Document" || currentPage == "Video"
          ? handleMultiSelectData()
          : handleSelectData();
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

        {data.thumbnail_url &&
        data.thumbnail_url !== "string" &&
        data.thumbnail_url !== null ? (
          <img src={data.thumbnail_url} alt="" />
        ) : (
          <img src="/avatarImg.png" alt="" />
        )}

        {/* image overlay content only for course,scenario,module */}
        {(currentPage == "Avatars Assigned" ||
          currentPage == "PersonaSelection") && (
          <div className={styles.details}>
            <div className={styles.title}>
              <p>Character Name</p>
              <div>{data?.name}</div>
            </div>
            <div className={styles.status}>
              {/* <p>Age</p>
              <div>{data?.age}</div> */}
            </div>
          </div>
        )}
          {(currentPage != "Document" && currentPage != "Video" && currentPage!="Languages Assigned" && currentPage!="Environments Assigned")&&<div
            className={styles.previewIcon}
            onClick={(e) => {
              e.stopPropagation()
              setIsPreview({enable:true,msg:data?.id,value:"AvatarPopUp"})
            }}
          >
            <PreviewIcon />
          </div>}
        {(!currentPage == "Languages Assigned" || currentPage == "PersonaSelection") && (
          <div className={styles.gradient}></div>
        )}
        {(currentPage == "Avatars Assigned") && (
          <div className={styles.gradient}></div>
        )}
      </div>
      {(currentPage != "Document" && currentPage != "Video")&&
        <div className={styles.contentContainer}>
          <div className={styles.titles}>
            {currentPage != "Environments Assigned" ? (
              <p>Role</p>
            ) : (
              <p>Environment</p>
            )}
            <div>{currentPage=="PersonaSelection"?data?.persona_type:data.name}</div>
          </div>
        </div>
      }
      {(currentPage === "Document" || currentPage === "Video")&&<div className={styles.titles}>
        {currentPage === "Document" ? (
          <p>Document Title</p>
        ) : currentPage === "Video" ? (
          <p>Video Title</p>
        ) : null}
            <div title={data?.title}>{data?.title?.length > 25 ? data?.title?.slice(0, 25)?.replaceAll(/[_-]/g, " ") + "..." : data.title?.replaceAll(/[_-]/g, " ")}</div>
            </div>}
    </div>
  );
}

export default AvatarCard;
