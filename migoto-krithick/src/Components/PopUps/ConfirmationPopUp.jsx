import React from "react";
import styles from "../PopUps/ContentPopUp.module.css"; 
import CloseRedIcon from "../../Icons/CloseRed";
import UsersIcon from "../../Icons/UsersIcon";
import { useLOIData, usePreviewStore } from "../../store";
import { useNavigate } from "react-router-dom";

function ConfirmationPopUp() {
  const { isPreview, setIsPreview } = usePreviewStore();
  const { selectedData, setSelectedData } = useLOIData();
  let navigate = useNavigate()

  let suitableName = {
    bulkPopUp:{
      current:"Course",
      color: "blue",
      header: "Bulk Assign",
      content:"Course will be assigned to all users uploaded from the document. Please double-check the data before proceeding with the Process",
      image:`/popupContent1.png`,
      onClick:`/migoto-cms/createUser/assignCourse/bulkAssign`,
    },
    deletePopUp:{
      current:"Module",
      color: "red",
      header: "Delete",
      content:"Are you sure you want to permanently delete this user from your assigned list? This action cannot be undone. The user’s course access and progress data will be lost. ",
      image:`/deletePopUp.png`,
      onClick:"createModule"
    },
    unAssignPopUp:{
      current:"Module",
      color: "blue",
      header: "Unassign",
      content:"Are you sure you want to unassign this user from Admin 1 assigned list? They will still have access to their courses and progress will be retained",
      image:`/UnassignPopUp.png`,
      onClick:"createModule"
    },
  }

  if(!isPreview?.enable || !["bulkPopUp", "deletePopUp", "unAssignPopUp"].includes(isPreview.value)){
    return null;
  }

  return (
    <div className={styles.bgContainer}>
    <div className={styles.bulkPopup}>
      <div
        className={styles.PopupHeader}
        onClick={() => {
          if (isPreview.resolve) isPreview.resolve(false);
          setIsPreview({ enable: false, msg: {}, value: "", resolve: null });
        }}
      >
        <div>
        <CloseRedIcon />
        </div>
      </div>
      <div className={styles.popUpImg}>
        <img src={suitableName[isPreview.value]?.image} alt="" />
      </div>

      <div className={styles.PopupContent}>
        <div className={styles[suitableName[isPreview.value]?.color]}>{suitableName[isPreview.value]?.header}</div>
        <p>
          {suitableName[isPreview.value]?.content}
        </p>
      </div>
      <div className={styles.PopupUser}>
        <div className={styles.leftContent}>
          <div>Selected Users :</div>
          <p className={styles.Count}>{isPreview.msg[0]}</p>
        </div>
        <div className={styles.rightContent}>
          <UsersIcon />
        </div>
      </div>
      <div className={styles.buttonGroup}>
        <button
          className={styles.cancelButton}
          onClick={() => {
            if (isPreview.resolve) isPreview.resolve(false);
            setIsPreview({ enable: false, msg: {}, value: "", resolve: null });
          }}
        >
          Cancel
        </button>
        <button
          className={styles.submitButton}
          onClick={() => {
            if (isPreview.resolve) isPreview.resolve(true);
            setIsPreview({ enable: false, msg: {}, value: "", resolve: null });
          }}
        >
          Confirm
        </button>
      </div>
    </div>
    </div>
  );
}

export default ConfirmationPopUp;
