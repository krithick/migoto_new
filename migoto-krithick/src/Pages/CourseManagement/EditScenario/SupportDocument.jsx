import React, { useEffect, useState } from "react";
import styles from "./SupportDocument.module.css";
import axios from "../../../service.js";
import BulkIcon from "../../../Icons/BulkIcon";
import { useLOIData } from "../../../store";
import PdfIcon from "../../../Icons/PdfIcon";
import RemoveButtonIcon from "../../../Icons/RemoveButtonIcon";
import { Button } from "antd";
import { getSessionStorage } from "../../../sessionHelper.js";

function SupportDocument({setEditPage, setCurrentPage}) {
  let [data, setData] = useState([]);
  const [uploadDoc, setUploadDoc] = useState(true);
  const { selectedData, setSelectedData } = useLOIData();
  const [docUploads, setDocUploads] = useState(
    // selectedData["EditingScenarioData"]?.knowledge_base?.documents
  );

  const handleFileChange = (event) => {
    setSelectedData("supportDocs", []);
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

  const removeDocuments = async (docId) => {
    const formData = new FormData();
    formData.append("action", "remove");
    formData.append("remove_doc_ids", docId);

    axios
      .put(
        `/knowledge-base/${selectedData["EditingScenarioData"]?.knowledge_base.id}/documents`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      )
      .then((res) => {
        console.log(res), fetch();
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const addDocuments = async (event) => {
    const files = Array.from(event.target.files); // Convert FileList to array


    if(selectedData["EditingScenarioData"]?.knowledge_base?.id && getSessionStorage("template_id")){
      const formData = new FormData();
      files.forEach((file) => formData.append("new_docs", file));  
      formData.append("action", "add");
    axios.put(`/knowledge-base/${selectedData["EditingScenarioData"]?.knowledge_base.id}/documents`,formData,{headers: {"Content-Type": "multipart/form-data",},})
      .then((res) => {fetch();})
      .catch((err) => {console.log(err)});
    }else{
      const formData = new FormData();
      files.forEach((file) => formData.append("supporting_docs", file));
      axios
      .post(
        `/knowledge-base/create/${getSessionStorage("template_id")}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      )
      .then((res) => {
        fetch();
      })
      .catch((err) => {
        console.log(err);
      });

    }

  };

  const fetch = () => {
    axios
      .get(`scenarios/${getSessionStorage("showScenario")}/editing-interface`)
      .then((res) => {
        setDocUploads(res.data.knowledge_base?.documents);
        setSelectedData("EditingScenarioData",res?.data)
      })
      .catch((res) => {
        console.log(err);
      });
  };

  useEffect(() => {
    fetch();
  }, []);

  return (
    <>
      <div className={styles.mainContainer1}>
        <div className={styles.uploadSection1}>
          <div className={styles.inputDiv}>
            <label htmlFor="">
              Remove or Upload Supporting Documents <span></span>
            </label>
          </div>
          <div className={styles.sections} style={{ justifyContent: "center" }}>
            <div className={styles.leftSection1}>
              <div
                className={styles.uploadContainer1}
                onDragOver={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    handleFileChange({
                      target: { files: e.dataTransfer.files },
                    });
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
                      onChange={addDocuments}
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
                {docUploads &&
                  docUploads.map((val, i) => (
                    <>
                      <div className={styles.uploadCard}>
                        <div className={styles.iconBg}>
                          <PdfIcon className={styles.pdfIcon} />
                        </div>
                        <div className={styles.titleContainer}>
                          <div className={styles.header}>Document Title</div>
                          <div className={styles.fileName}>{val.filename}</div>
                        </div>
                        <div
                          className={styles.removePart}
                          onClick={() => {
                            removeDocuments(val._id);
                          }}
                        >
                          <RemoveButtonIcon />
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
          <div className={styles.nextPageBtn}>
            <Button type="primary" onClick={()=>{setEditPage(),setSelectedData("showScenario",null)}}>Back</Button>
            <Button type="primary" onClick={()=>{setCurrentPage(),setSelectedData("showScenario",null),localStorage.setItem("flow","CourseManagement flow")}}>Next</Button>
          </div>
        </div>
      </div>
    </>
  );
}

export default SupportDocument;
