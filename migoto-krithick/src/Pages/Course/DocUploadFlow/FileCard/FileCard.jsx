import React, { useEffect, useState } from "react";
import styles from "./FileCard.module.css";
import PdfIcon from "../../../../Icons/PdfIcon";
import PlayIcon from "../../../../Icons/PlayIcon";
import { Progress } from "antd";
import axios from "../../../../service";
import { useLOIData } from "../../../../store";

export default function FileCard({ doc, file, onUploadComplete,currentPage,setCheckUpdate }) {
  const [progress, setProgress] = useState(file.progress);
  let { selectedData, setSelectedData } = useLOIData();

  useEffect(() => {
    if (["Completed", "done"]?.includes(file.status)) {
      return;
    }
    uploadFile();
  }, []);
// console.log(currentPage);

const postData = (url,data) => {

  let payload;
  if(url=="/videos/"){
    payload = {
      title: data?.original_filename,
      url: data?.live_url,
      description:data?.description,
      duration: 0,
      thumbnail_url: "https://meta.novactech.in/thumbnail/thumbnail_video.png"    
    }

  }else{
    payload = {
      title: data?.original_filename,
      file_url: data?.live_url,
      file_type: data?.file_type,
      description: data?.description,
      thumbnail_url: `https://meta.novactech.in:7445/uploads/image/20250508064123_1935338b.png`,
    }
  }


  let Auth = localStorage.getItem("migoto-cms-token");

  axios.post(url,payload)
  .then((res)=>{
    setCheckUpdate()
  }).catch((err)=>{console.log(err);
  })
}


  const uploadFile = async () => {

    const formData = new FormData();
    formData.append("file", file.file);
    formData.append("file_type", doc ? "document" : "video");

    let Auth = localStorage.getItem("migoto-cms-token");
    const headers = {
      "Content-Type": "multipart/form-data",
      authorization: Auth,
    };

    axios
      .post("/uploads/", formData, {
        headers,
        onUploadProgress: (e) => {
          const percent = Math.round((e.loaded * 100) / e.total);
          setProgress(percent);
        },
      })
      .then((res) => {
        if (onUploadComplete) {
          onUploadComplete(file.id, {
            status: "done",
            progress: 100,
            serverResponse: res.data,
          });
        }

        // for setting in the zustand
        const currentData = useLOIData.getState().selectedData;

        if (doc) {
          if(currentPage!="supportDocs"){
            const existingDocs = currentData.assignedDocument || [];
            useLOIData
              .getState()
              .setSelectedData("assignedDocument", [
                ...existingDocs,
                res.data.id,
              ]);
              postData("/documents/",res.data)
          }else{
            const existingDocs = currentData.supportDocs || [];
            useLOIData
              .getState()
              .setSelectedData("supportDocs", [
                ...existingDocs,
                res.data.id,
              ]);
          }
        } else {
          const existingVideos = currentData.assignedVideo || [];
          useLOIData
            .getState()
            .setSelectedData("assignedVideo", [...existingVideos, res.data.id]);
            postData("/videos/",res.data)
        }
      })
      .catch((err) => {
        console.error("Upload error", err);
        if (onUploadComplete) {
          onUploadComplete(file.id, {
            status: "error",
            progress: 0,
          });
        }
      });
  };

  return (
    <div className={styles.uploadCard}>
      <div className={styles.iconBg}>
        {doc ? (
          <PdfIcon className={styles.pdfIcon} />
        ) : (
          <PlayIcon className={styles.playIcon} />
        )}
      </div>
      <div className={styles.titleContainer}>
        <div className={styles.header}>{doc ? "Document" : "Video"} Title</div>
        <div className={styles.fileName}>{file.name}</div>
        <div className={styles.progressContainer}>
          <Progress
            percent={progress}
            // status={file.status === "error" ? "exception" : "active"}
          />
        </div>
      </div>
    </div>
  );
}
