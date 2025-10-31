import React from "react";
import styles from "../CourseManagement/DetailCard.module.css"
import AIicon from "../../Icons/AIicon";
import EditIcon from "../../Icons/EditIcon";
import DeleteIcon from "../../Icons/DeleteIcon";
import { useNavigate } from "react-router-dom";
import { useLOIData } from "../../store";
import { getSessionStorage, setSessionStorage } from "../../sessionHelper";

function DetailCard({courseDetail, currentPage, setCurrentPage,setPage}) {
    let navigate = useNavigate();
  const { selectedData, setSelectedData } = useLOIData();

    let suitableName = {
        showCourse:{
          current:"Course",
          create: "Create Course",
          header: "List of Courses",
          detailHeader:"",
          edit:"editCourse"
        },
        showModule:{
          current:"Module",
          create: "Create Module",
          header: "List of Modules",
          detailHeader:"Course ",
          edit:"editCourse",
          flow: "CourseManagement & editCourse flow"
        },
        showScenario:{
          current:"Scenario",
          create: "Create Scenario",
          header: "List of Scenarios",
          detailHeader: "Module ",
          edit:"editModule",
          flow: "CourseManagement & editModule flow"
        },
        showAvatarInteraction:{
          current:"AvatarInteraction",
          create: "Create Scenario",
          header: "Avatar Interaction",
          detailHeader: "Scenario ",
          edit:"editScenario",
          flow: "CourseManagement & editScenario flow"
        }
      }

      let userEmpId = JSON.parse(localStorage.getItem("user"))?.id;

    return (
        <div className={styles.main}>
            {false &&<div className={styles.aiBanner}>
                <div className={styles.aiSvg}><AIicon/></div>
                <div className={styles.aiTitle}>Generated in AI</div>
            </div>}

            <div className={styles.editBtn}>
            {/* <div className={styles.editSvg}><DeleteIcon/></div> */}
            </div>

            <div className={styles.thumbnail}>
                 <img src={courseDetail?.thumbnail_url} alt="Image" />
            </div>

            <div className={styles.content}>
                <div className={styles.contentSnips}>
                        <div className={styles.snip}>
                            <p className={styles.snipTitle}>{suitableName[currentPage].detailHeader}Title</p>
                            <p className={styles.snipContent}>{courseDetail?.title}</p>
                        </div>
                        <div className={styles.snip}>
                            <p className={styles.snipTitle}>created By</p>
                            <p className={styles.snipContent}>{courseDetail?.creater_role?courseDetail?.creater_role:courseDetail?.created_by_info?courseDetail?.created_by_info?.role : "NA"}</p>
                            {/* <p className={styles.snipContent}>{courseDetail?.creater_role?courseDetail?.creater_role:courseDetail?.created_by}</p> */}
                        </div>
                        <div className={styles.snip}>
                            <p className={styles.snipTitle}>{suitableName[currentPage].detailHeader}Code</p>
                            <p className={styles.snipContent}>{courseDetail?.id?.slice(courseDetail?.id?.length-5)}</p>
                        </div>
                </div>

                <div className={styles.descriptionBox}>
                    <p className={styles.descTitle}>Description</p>
                    <p className={styles.descContent}>
                        {courseDetail?.description}
                    </p>
                </div>
                <div className={styles.btnGrp}>
                    {/* <button className={styles.assign} onClick={()=>{}}>Assign</button> */}
                    {(userEmpId==courseDetail?.created_by)&& currentPage!="showAvatarInteraction" &&<button onClick={()=>{setCurrentPage(suitableName[currentPage].edit),setPage("baseDocument"),localStorage.setItem("flow",suitableName[currentPage].flow)}}>Edit <EditIcon/></button>}
                    {(userEmpId==courseDetail?.created_by)&& (currentPage=="showAvatarInteraction"&& getSessionStorage("template_id"))&&<button onClick={()=>{setCurrentPage(suitableName[currentPage].edit),setPage("baseDocument"),localStorage.setItem("flow",suitableName[currentPage].flow)}}>Edit <EditIcon/></button>}
                    {(userEmpId==courseDetail?.created_by && (currentPage=="showAvatarInteraction"&& getSessionStorage("template_id")))&&<button onClick={()=>{setCurrentPage(suitableName[currentPage].edit),setPage("editBaseDetail"),localStorage.setItem("flow",suitableName[currentPage].flow)}}>Edit Base Details<EditIcon/></button>}
                    {(userEmpId==courseDetail?.created_by && (currentPage=="showAvatarInteraction"&& getSessionStorage("template_id"))) && <button onClick={()=>{setCurrentPage(suitableName[currentPage].edit),setPage("personaPopUp"),localStorage.setItem("flow",suitableName[currentPage].flow),setSessionStorage("AvatarAssignedTo","all")}}>Create avatar<EditIcon/></button>}
                </div>
            </div>
        </div>  
    );
}

export default DetailCard;
