import React, { useEffect, useState } from "react";
import styles from "../../DocUploadFlow/Doc.module.css";

import axios from "../../../../service";
import PlusIcon from "../../../../Icons/PlusIcon";
import BulkIcon from "../../../../Icons/BulkIcon";
import { useLOIData } from "../../../../store";
import AvatarCard from "../../../../Components/ModesComponent/AvatarCard";
import { Button } from "antd";
import FileCard from "../../DocUploadFlow/FileCard/FileCard";
import PdfIcon from "../../../../Icons/PdfIcon";

function SupportDocUpload() {
  let [data, setData] = useState([]);
  const [uploadDoc, setUploadDoc] = useState(true);
  const { selectedData, setSelectedData } = useLOIData();
  const [docUploads, setDocUploads] = useState([]);


  const handleFileChange = (event) => {
    setSelectedData("supportDocs",[])
    const files = Array.from(event.target.files); // Convert FileList to array
    if (!files.length) return;

    const newUploads = files.map((file) => ({
      id: Date.now() + Math.random(), // unique ID
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      progress: 0,
      status: "pending",
    }));

    if (uploadDoc) {
      setDocUploads((prev) => [...prev, ...newUploads]);
      const existingSupportDocs = selectedData["supportDocs"] || [];
      setSelectedData("supportDocs", [...existingSupportDocs, ...files]);
    }
  };

  return (
    <>
      <div className={styles.mainContainer1}>
        <div className={styles.uploadSection1}>
          <div className={styles.inputDiv}>
            <label htmlFor="">Upload Supporting Documents <span></span></label>
          </div>
          <div className={styles.sections} style={{ justifyContent: "center" }}>
            <div className={styles.leftSection1}>
              <div className={styles.uploadContainer1}
              onDragOver={(e) => {
                e.preventDefault();
                e.stopPropagation();
              }}
              onDrop={(e) => {
                e.preventDefault();
                e.stopPropagation();
                if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                  handleFileChange({ target: { files: e.dataTransfer.files } });
                  e.dataTransfer.clearData();
                }
              }}
              >
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
                      multiple
                      accept=".pdf, .doc, .docx" // need to change the format based on the file format
                      style={{ display: "none" }}
                    />
                  </label>
                  <div className={styles.iconContainer}>
                    {/* <ReactSVG src="/bulk.svg" /> */}
                    <BulkIcon />
                  </div>
                  <h3 className={styles.title}>Upload Document from files</h3>
                  <p className={styles.subtitle}>Drag and drop here</p>
                </div>
              </div>
              <div className={styles.uploadFiles}>
                {uploadDoc &&
                  docUploads &&
                  docUploads.map((val, i) => (
                    <>
                      <div className={styles.uploadCard}>
                        <div className={styles.iconBg}>
                      
                            <PdfIcon className={styles.pdfIcon} />
                        
                        </div>
                        <div className={styles.titleContainer}>
                          <div className={styles.header}>
                            Document Title
                          </div>
                          <div className={styles.fileName}>{val.name}</div>
                         
                        </div>
                      </div>

                      {/* <FileCard
                        key={i}
                        file={val}
                        doc={true}
                        onUploadComplete={handleUploadComplete}
                        currentPage={"supportDocs"}
                      /> */}
                    </>
                  ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default SupportDocUpload;
