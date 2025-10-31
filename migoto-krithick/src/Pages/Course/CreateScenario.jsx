import React, { useEffect, useState } from "react";
import styles from "./CreateCourse.module.css";
import CourseForm from "./CourseForm";
import DocumentUploadFlow from "./DocUploadFlow/DocumentUploadFlow";
import { useLOIData } from "../../store";
import { Navigate, useNavigate } from "react-router-dom";
import AiScenarioBuilder from "./AIScenario/AiScenarioBuilder";
import EditDocument from "./AIScenario/EditDocument/EditDocument";
import EditDocument2 from "./AIScenario/EditDocument/EditDocument2";
import { getSessionStorage } from "../../sessionHelper";

function CreateScenario({currentPage,setCurrentPage,data,setData,moveTo}) {

  const [uploadPage, setUploadPage] = useState("Image Upload")
  let {selectedData, setSelectedData} = useLOIData();
  let navigate = useNavigate();
  let flow = localStorage.getItem("flow");

  useEffect(()=>{
    if(moveTo){
      setUploadPage("Document Upload")
    }
  },[moveTo])

        useEffect(() => {
          if (flow == "CourseManagement flow" && getSessionStorage("showCourse") && getSessionStorage("showModule")) {
            setSelectedData("courseId", getSessionStorage("showCourse"));
            setSelectedData("moduleId", getSessionStorage("showModule"));
            sessionStorage.setItem("courseId", getSessionStorage("showCourse"));
            sessionStorage.setItem("moduleId", getSessionStorage("showModule"));
          }
        }, []); //corseManagement flow creating module without creating course
  

      return (
    <>
      <div className={styles.createCourseContainer}>
        {uploadPage!="CreateAIScanario" &&<div className={styles.header}>
          <div className={styles.page}>
            <div className={styles.currentPage}>Create Scenario</div>
            {uploadPage=="Image Upload" && <button onClick={()=>{setUploadPage("CreateAIScanario"),setSelectedData("supportDocs",null),setSelectedData("avatarSelection",null)
              setSelectedData("ListofAvatars",null)}} className={styles.gnrBtn}> Create scenario with AI</button>}
          </div>
        </div>}
        {uploadPage=="Image Upload" && <CourseForm setUploadPage={(item)=>{setUploadPage(item)}} setCurrentPage={()=>{setCurrentPage("Create Module")}}/>}
        {uploadPage=="CreateAIScanario" && <AiScenarioBuilder setUploadPage={(item)=>{setUploadPage(item)}} currentPage={currentPage}  setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>}
        {/* {uploadPage=="DataEdition" && <EditDocument setUploadPage={(item)=>{setUploadPage(item)}} />}
        {uploadPage=="Document Upload" && <DocumentUploadFlow currentPage={"Course Doc Upload"} setCurrentPage={()=>{setCurrentPage("avatarSelection")}} setUploadPage={()=>{setUploadPage("DataEdition")}}/>} */}
      </div>
    </>
  );
}

export default CreateScenario;