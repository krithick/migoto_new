import { useState } from "react";
import styles from "../../../../Components/UplaodAction/Upload/Bulk.module.css";
import DownloadIcon from "../../../../Icons/DownloadIcon";
import WarningIcon from "../../../../Icons/WarningIcon";
import BulkIcon from "../../../../Icons/BulkIcon";
import { useNavigate } from "react-router-dom";
import Papa from "papaparse";
import { useUserPopupStore } from "../../../../store";

export default function BulkAdmin() {
  const navigate = useNavigate();
  const { message, setMessage } = useUserPopupStore();
  const csvUploadFn = (e) => {
    const file = e.target.files[0];
    if (file) {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: function (results) {
          navigate("/migoto-cms/bulkAdminList", { state: { data: results.data, fileName: file.name } });
        },
      });
    }
  };

  return (
    <div className={styles.manualUploadContainer}>
      <div className={styles.manualUploadHeader}>
        <h2>Bulk Upload</h2>
        <button
          onClick={() => {
            const link = document.createElement("a");
            link.href = "/admin_template.csv";
            link.download = "admin_template.csv";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          }}
        >
          Download Template <DownloadIcon />
        </button>
      </div>

      <div className={styles.manualForm}>
        <div className={styles.FileContainer}>
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
            <input id="file-upload" type="file" onChange={csvUploadFn} accept=".csv" style={{ display: "none" }} />
          </label>
          <div className={styles.iconContainer}>
            <BulkIcon />
          </div>
          <h3 className={styles.title}>Upload Document from files</h3>
          <p className={styles.subtitle}>Drag and drop here</p>
        </div>
        <div className={styles.instructionContainer}>
          <div className={styles.instruction}>
            <WarningIcon />
            <p>Instruction :</p>
          </div>
          <div className={styles.instructionPoint}>
            <p>Download the Template File and fill it with proper data</p>
            <p>Once you have downloaded and filled the Template file, upload it</p>
            <p>
              It is important to follow the same format as the Template, wrongly formatted files will not be processed
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}