import React, { useEffect } from "react";
import styles from "../LVESelection/LVECard.module.css";
import { useLangStore, useLOIData, useModeData } from "../../../store";

function LVECard({ data, currentPage, index, setActiveState }) {
  const { selectedData, setSelectedData } = useLOIData();
  const { isOpen, setIsOpen } = useModeData();
  const { localLang, setLocalLang } = useLangStore();

  //   const handleSelectData = () =>{
  //     if(selectedData[currentPage]==data.id){
  //       setSelectedData(currentPage,null);
  //     }else{
  //       setSelectedData(currentPage,data.id)
  //     }
  //   }

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
  
  const handleSelectCode = () => {
    //card selection
    const currentData = selectedData[currentPage] || [];

    let updatedData;

    const toggleCodeInList = (localLang, id) => {
      if (localLang?.includes(id)) {
        // Remove item
        return localLang.filter((item) => item !== id);
      } else {
        // Add item
        return [...localLang, id];
      }  
    };

    const updatedDatas = toggleCodeInList(localLang, data?.id);

    
    if (currentData?.includes(data?.code)) {
      // Remove item
      updatedData = currentData.filter((code) => code !== data?.code);
    } else {
      // Add item
      updatedData = [...currentData, data?.code];
    }
    setSelectedData(currentPage, updatedData);
    setLocalLang(updatedDatas);
  };

  return (
    <div
      className={`${
        currentPage == "Course Doc Upload" ? styles.cardModify : styles.card
      } ${
        (
          currentPage == "Language"
            ? selectedData[currentPage]?.includes(data?.code)
            : selectedData[currentPage]?.includes(data?.id)
        )
          ? styles.activeCard
          : ""
      }`}
      onClick={() => {
        currentPage == "Language" ? handleSelectCode() : handleSelectData();
      }}

    >
      <div
        className={`${styles.imgContainer} ${
          currentPage == "DocumentFile"
            ? styles.PdfContainer
            : styles.videoContainer
        }`}
      >
        {<img src={data?.thumbnail_url} alt="" />}

        {/* {(currentPage == 'Avatars Assigned'|| currentPage == 'PersonaSelection') && <div className={styles.details}> 
          <div className={styles.title}>
            <p>Character Name</p>
            <div>{data?.persona_id[0]?.name}</div>
          </div>
          <div className={styles.status}>
            <p>Age</p>
            <div>{data.age}
            </div>
          </div>
        </div>} */}
        {/* {(!currentPage == "Course Doc Upload")&&<div className={styles.previewIcon} onClick={()=>{setActiveState()}}><PreviewIcon /></div>}
       {(!currentPage == "Languages Assigned")&&<div className={styles.gradient}></div>} */}
      </div>
      {
        <div
          className={styles.contentContainer}
        >
          <div className={styles.titles}>
            {currentPage != "Environment" ? <p>Role</p> : <p>Environment</p>}
            <div>{data?.name}</div>
          </div>
        </div>
      }
    </div>
  );
}

export default LVECard;
