// import React from "react";
// import styles from "../PopUps/BulkPopup.module.css";
// import CloseRedIcon from "../../Icons/CloseRed";
// import UsersIcon from "../../Icons/UsersIcon";
// import { useLOIData, usePreviewStore } from "../../store";
// import { useNavigate } from "react-router-dom";

// function BulkPopUp() {
//   const { isPreview, setIsPreview } = usePreviewStore();
//   const { selectedData, setSelectedData } = useLOIData();
//   let navigate = useNavigate()
//   return (
//     <div className={styles.bulkPopup}>
//       <div
//         className={styles.PopupHeader}
//         onClick={() => {
//           setIsPreview({ enable: false, msg: {}, value: "bulkPopUp" });
//         }}
//       >
//         <CloseRedIcon />
//       </div>
//       <div className={styles.popUpImg}>
//         <img src="/popupContent1.png" alt="" />
//       </div>

//       <div className={styles.PopupContent}>
//         <div>Bulk Assign</div>
//         <p>
//           Course will be assigned to all users uploaded from the document.
//           Please double-check the data before proceeding with the Process
//         </p>
//       </div>
//       <div className={styles.PopupUser}>
//         <div className={styles.leftContent}>
//           <div>Selected Users :</div>
//           <p className={styles.Count}>{isPreview.msg[0]}</p>
//         </div>
//         <div className={styles.rightContent}>
//           <UsersIcon />
//         </div>
//       </div>
//       <div className={styles.buttonGroup}>
//         <button
//           className={styles.cancelButton}
//           onClick={() => {
//             setIsPreview({ enable: false, msg: {}, value: "bulkPopUp" });
//             navigate(-1);
//           }}
//         >
//           Cancel
//         </button>
//         <button
//           className={styles.submitButton}
//           onClick={() => {
//             navigate(`/migoto-cms/createUser/assignCourse/bulkAssign`),
//               setIsPreview({ enable: false, msg: {}, value: "bulkPopUp" });
//           }}
//         >
//           Confirm
//         </button>
//       </div>
//     </div>
//   );
// }

// export default BulkPopUp;
