import React, { useEffect, useState } from "react";
import styles from "./Doc.module.css";
import PlusIcon from "../../../Icons/PlusIcon";
import BulkIcon from "../../../Icons/BulkIcon";
import FileCard from "./FileCard/FileCard";
import { Button } from "antd";
import AvatarCard from "../../../Components/ModesComponent/AvatarCard";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../../store";
import axios from '../../../service'
import { Navcontent } from "../../Sidebar/SidebarPopUpContent";
import { useNavigate } from "react-router-dom";
import { UpdateTimeline } from "../../../Components/Timeline/UpdateTImeLine";
import { setSessionStorage } from "../../../sessionHelper";

function DocumentUploadFlow({ currentPage, setCurrentPage,setUploadPage }) {
 const [checkUpdate, setCheckUpdate] = useState(false)
  let [data, setData] = useState([]);
  // const [currentPage, setCurrentPage] = useState("Course Doc Upload");
  const [uploadDoc, setUploadDoc] = useState(true);
  const {selectedData, setSelectedData} = useLOIData();
  const [vidUploads, setVidUploads] = useState([]);
  const [docUploads, setDocUploads] = useState([]);
  const { message, setMessage } = useUserPopupStore();
  let navigate = useNavigate()
  const { isPreview, setIsPreview } = usePreviewStore();

  const fetchDocument = async () => {    
      try{
            const documents = await axios.get("/documents/")
            setData(documents.data)
        }catch(e){
            console.log("Unable to fetch documents",e);
        }
  }

  const fetchVideos = async () => {
      try{
            const videos = await axios.get("/videos/")
            setData(videos.data)
            
        }catch(e){
            console.log("Unable to fetch documents",e);
        }
  }
  
    useEffect(() => {
        if(uploadDoc){
          fetchDocument()
        }else {
          fetchVideos()
        }
    }, [uploadDoc,checkUpdate])

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const newUpload = {
      id: Date.now(), // unique ID for tracking
      file: file,
      name: file.name,
      size: file.size,
      type: file.type,
      progress: 0,
      status: "pending", // you can use 'pending', 'uploading', 'done', etc.
    };
    if (uploadDoc) {
      setDocUploads((prevDocUploads) => [...prevDocUploads, newUpload]);
    } else {
      setVidUploads((prevVidUploads) => [...prevVidUploads, newUpload]);
    }
  };
  const handleUploadComplete = (id, updatedData) => {
    const updateList = (listSetter, uploads) => {
      listSetter(
        uploads.map((item) =>
          item.id === id ? { ...item, ...updatedData } : item
        )
      );
    };

    if (uploadDoc) {
      updateList(setDocUploads, docUploads);
    } else {
      updateList(setVidUploads, vidUploads);
    }
  };

  // useEffect(()=>{
  //   if(selectedData["Document"]?.length>0){
  //     setUploadDoc(false)
  //   }
  // },[selectedData["Document"]])



  const handleNextPage = () =>{
    setUploadDoc(false)
  }

  const handleNext = () =>{
    let path = window.location.pathname;
    const cleanedPath = path?.replace("/videoPdf", "/personaCreation");
    navigate(cleanedPath)
  }

    const checkNavigation = () => {
      let result = new Promise((resolve) => {
        setIsPreview({
          enable: true,
            msg: `${Navcontent[window.location.pathname]?Navcontent[window.location.pathname]:"Are you sure you want to proceed with this action?"}`,
          value: "ok/cancel",
          resolve,
        });
      });
      result.then((res) => {
        if (res) {
          navigate(-1)
          UpdateTimeline(4, {
            status: "error",
            description: ``
          },setSelectedData);
          UpdateTimeline(3, {
            status: "warning",
            description: `In Progress`
          },setSelectedData);
          
        }
      });
    };

    useEffect(()=>{
      setSessionStorage("Document",selectedData["Document"])
      setSessionStorage("Video",selectedData["Video"])  
    },[selectedData["Video"],selectedData["Document"]])
  

  return (
    <>
      <div className={styles.mainContainer}>
      <div className={styles.headers}>
          <div className={styles.page}>
            <div className={styles.currentPage}>Create Scenario</div>
          </div>
        </div>

        <div className={styles.header}>
          <span className={styles.title}>Upload Document & Video</span>
          <br />
          <span className={styles.subTitle}>
            {/* Upload the same Document/Video converted into each selected language
            under the tabs below before assigning */}
            Select videos and documents to enhance users learning experience for Learn Mode 
          </span>
        </div>
        <div className={styles.uploadSection}>
          <div className={styles.fileType}>
            <button
              className={`${styles.fileTypeBtn}  ${
                uploadDoc ? styles.active : ""
              }`}
              onClick={() => setUploadDoc(true)}
            >
              <PlusIcon /> Document & PDF
            </button>
            <button
              className={`${styles.fileTypeBtn}  ${
                !uploadDoc ? styles.active : ""
              }`}
              onClick={() => setUploadDoc(false)}
            >
              <PlusIcon /> Video File
            </button>
          </div>
          <div className={styles.sections1}>
            <div className={styles.leftSection}>
              <span>Upload {uploadDoc ? "Document" : "Video"}</span>
              <div className={styles.uploadContainer}>
                <div className={styles.fileContainer}>
                  <label
                    htmlFor="file-upload"
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      width: "100%",
                      height: "100%",
                      cursor: "pointer",
                      opacity: 0,
                      zIndex: 1,
                      backgroundColor: "red",
                    }}
                  >
                    <input
                      id="file-upload"
                      type="file"
                      onChange={handleFileChange}
                      accept={uploadDoc ? ".pdf" : ".mp4"} // need to change the format based on the file format
                      style={{ display: "none" }}
                    />
                  </label>
                  <div className={styles.iconContainer}>
                    {/* <ReactSVG src="/bulk.svg" /> */}
                    <BulkIcon />
                  </div>
                  <h3 className={styles.title}>
                    Upload {uploadDoc ? "Document" : "Video"} from files
                  </h3>
                  {/* <p className={styles.subtitle}>Drag and drop here</p> */}
                </div>
              </div>
              <div className={styles.uploadFiles}>
                {uploadDoc &&
                  docUploads &&
                  docUploads.map((val, i) => (
                    <>
                      <FileCard
                        key={i}
                        file={val}
                        doc={true}
                        onUploadComplete={handleUploadComplete}
                        currentPage="assignedDocument"
                        setCheckUpdate={()=>{setCheckUpdate(!checkUpdate)}}
                      />
                    </>
                  ))}
                {!uploadDoc &&
                  vidUploads &&
                  vidUploads.map((val, i) => (
                    <>
                      <FileCard
                        key={i}
                        file={val}
                        doc={false}
                        onUploadComplete={handleUploadComplete}
                        currentPage="assignedVideo"
                        setCheckUpdate={()=>{setCheckUpdate(!checkUpdate)}}
                      />
                    </>
                  ))}
              </div>
            </div>
            <div className={styles.rightSection}>
              <div className={styles.docContainer}>
                <div className={styles.docheader}>
                  <span className={styles.title}>
                    Uploaded {uploadDoc ? currentPage="Document" : currentPage="Video"}
                  </span>
                  <div className={styles.body}>
                    {data.map((item, index) => {
                      return (
                        <AvatarCard
                          data={item}
                          key={index}
                          currentPage={currentPage}
                        />
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.footer}>
            <Button className={styles.cancelBtn} onClick={()=>{checkNavigation()}}>{"< Back"}</Button>
            {(uploadDoc)&&<Button
              className={styles.primaryBtn}
              type="primary"
              onClick={() => {
                handleNextPage()
              }}
            >
              {selectedData["Document"]?.length>0?"Next >":"Skip Document >"}
            </Button>}
            {(!uploadDoc)&&<Button
              className={styles.primaryBtn}
              type="primary"
              onClick={() => {
                handleNext()
              }}>
              {selectedData["Video"]?.length>0?"Next >":"Skip Video >"}
            </Button>}
          </div>
        </div>
      </div>
    </>
  );
}

export default DocumentUploadFlow;
