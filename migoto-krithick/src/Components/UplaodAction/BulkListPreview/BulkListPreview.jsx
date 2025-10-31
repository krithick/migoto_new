import React, { useState } from "react";
import styles from "../BulkListPreview/BulkListPreview.module.css";
import RemoveButtonIcon from "../../../Icons/RemoveButtonIcon";
import ReUploadBtnIcon from "../../../Icons/ReUploadBtnIcon";
import axios from "../../../service";
import { useNavigate, useLocation } from "react-router-dom";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../../store";
import { TimeLineRoute } from "../../../RouteHelper/TimeLineRoute";
import { UpdateTimeline } from "../../Timeline/UpdateTImeLine";
import { setSessionStorage } from "../../../sessionHelper";
import BackIcon from "../../../Icons/BackIcon";
import BulkIcon from "../../../Icons/BulkIcon";

function BulkListPreview() {
  const navigate = useNavigate();
  const location = useLocation();
  const { data = [], fileName = "Bulk_Upload.csv" } = location.state || {};
  const {isPreview, setIsPreview} = usePreviewStore();
  const { message, setMessage } = useUserPopupStore();
  const [selectedData1, setSelectedData1] = useState(data.map((item) => item.emp_id));
  let { selectedData, setSelectedData } = useLOIData();

  const handleAllSelect = (e) => {
    if (e.target.checked) {
      setSelectedData1(data.map((item) => item.emp_id));
    } else {
      setSelectedData1([]);
    }
  };

  const handleIndividualSelect = (empId, e) => {
    if (e.target.checked) {
      setSelectedData1((prev) => [...prev, empId]);
    } else {
      setSelectedData1((prev) => prev.filter((id) => id !== empId));
    }
  };

  const handleSaveUsers = async (type) => {
    try {
      let company_id = JSON.parse(localStorage.getItem("user"))?.company_id;

      const filteredUsers = data?.filter((item) => selectedData1?.includes(item.emp_id));

      const formattedPayload = filteredUsers.map((user) => ({
        username: user.username,
        emp_id: user.emp_id,
        email: user.email,
        password: user.password,
        is_active: user.status?.toLowerCase() === "active",
        role: "user",
        company_id:company_id,
        // assigneeEmpId: user.assigneeEmpId, // if backend accepts this
      }));

      const response = await axios.post("/auth/users", formattedPayload);
      const createdUsers = response.data;
      
      // localStorage.setItem("createdUser", JSON.stringify(createdUsers.map((item)=>item.id)));
      sessionStorage.setItem("createdUser", JSON.stringify(createdUsers.map((item)=>item.id)));
      setMessage({
        enable: true,
        msg: "Users Created Successfully",
        state: true,
      })      

      if (type === "save") {
        navigate(-1);
      } else {
        localStorage.setItem("TLData",JSON.stringify(TimeLineRoute["/migoto-cms/createUser/assignCourse/:id"]))
        
        const result = await new Promise((resolve) => {
          setIsPreview({
            enable: true,
            msg: [createdUsers?.length],
            value: "bulkPopUp",
            resolve
          });
        });
        
        if (result) {
          localStorage.setItem("currentPathLocation", "Assign Course");
          UpdateTimeline(1, {
            status: "success",
            description: `Users Created`
          },setSelectedData);
          UpdateTimeline("Course Selection", {
            status: "warning",
            description: `In Progress`
          },setSelectedData);
          navigate("/migoto-cms/createUser/assignCourse/bulkAssign");
        }
      }
    } catch (error) {
      console.error("Error saving bulk users:", error);
      setMessage({
        enable: true,
        msg: "Something went wrong",
        state: false,
      })
    }
  };

  return (
    <div className={styles.BulkPreviewContainer}>
      <div className={styles.BulkPreviewHead}>
        <div onClick={()=>{navigate(-1)}}>
          <BackIcon />
        </div>
        <p>Bulk Upload</p>
      </div>

      <div className={styles.pdfContainer}>
        <div className={styles.pdfSectionLeft}>
          <p>Uploaded File Name</p>
          <div>{fileName}</div>
        </div>
        <div className={styles.pdfSectionRight}>
          {/* <button className={styles.removeBtn} onClick={() => navigate("/migoto-cms/createUser")}>
            <RemoveButtonIcon /> Remove
          </button> */}
          <button className={styles.reuploadBtn} onClick={() => navigate("/migoto-cms/createUser")}>
            <ReUploadBtnIcon /> Re-upload
          </button>
        </div>
      </div>

      <div className={styles.previewContainer}>
        <div className={styles.previewContainerHeader}>
          <div className={styles.sideOne}>
            <p>Preview Of Uploaded Data</p>
            <div className={styles.countUser}>
              <div>Uploaded Users:</div>
              <span>{data?.length}</span>
              <div> | Selected:</div>
              <span>{selectedData1?.length}</span>
            </div>
          </div>
        </div>

        <div className={styles.previewContainerTable}>
          <table>
            <thead>
              <tr>
                <th>
                  <input
                    type="checkbox"
                    checked={selectedData1?.length === data?.length && data?.length > 0}
                    onChange={handleAllSelect}
                  />{" "}
                  S.no
                </th>
                <th>User Name</th>
                <th>Employee ID</th>
                <th>Email Address</th>
                <th>Password</th>
                {/* <th>Assignee Emp ID</th> */}
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index}>
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedData1?.includes(item.emp_id)}
                      onChange={(e) => handleIndividualSelect(item.emp_id, e)}
                    />{" "}
                    {index + 1}
                  </td>
                  <td>{item.username}</td>
                  <td>{item.emp_id}</td>
                  <td>{item.email}</td>
                  <td>{item.password}</td>
                  {/* <td>{item.assigneeEmpId}</td> */}
                  <td>{item.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className={styles.footer}>
        <button onClick={() => handleSaveUsers("save")}>Save</button>
        <button onClick={() => handleSaveUsers("assign")}>Save & Assign Course</button>
      </div>
    </div>
  );
}

export default BulkListPreview;
