import { useState } from "react";
import styles from "./EditUser.module.css";
import { useNavigate } from "react-router-dom";
import { useLOIData, useUserPopupStore } from "../../../store";
import axios from '../../../service.js'
import BackIcon from "../../../Icons/BackIcon.jsx";
import { getSessionStorage, setSessionStorage } from "../../../sessionHelper.js";

export default function EditUser() {
  const { message, setMessage } = useUserPopupStore();
  const navigate = useNavigate();
  let { selectedData, setSelectedData } = useLOIData();
  let val = getSessionStorage("userData")?.data
  const [formData, setFormData] = useState({
    username: getSessionStorage("userData")?.data?.username??"",
    emp_id: getSessionStorage("userData")?.data?.emp_id??"",
    email: getSessionStorage("userData")?.data?.email??"",
    is_active: getSessionStorage("userData")?.data?.is_active??true,
    role: "user",
    account_type: getSessionStorage("userData")?.data?.account_type??"regular",
    demo_expires_at: getSessionStorage("userData")?.data?.demo_expires_at??new Date("01-01-2027"),
  });

  const isFormValid =
    formData.username.trim() !== "" &&
    formData.emp_id.trim() !== "" &&
    formData.email.trim() !== "" ;

  const handleChange = (e) => {
    const { name, value, type } = e.target;

    let newValue = value;
    
    if (name === "is_active") {
      newValue = value === "true";
    }

    setFormData({
      ...formData,
      [name]: newValue,
    });
  };

  const handleSubmit = (e, type) => {
    e.preventDefault();
    axios
      .put(`/auth/users/${val.id}`, formData)
      .then((res) => {
        console.log('res: ', res.data);
        setSelectedData("userRefresh", Date.now());
        setSessionStorage("userData", res);
        setMessage({
          enable: true,
          msg: "User Edited Successfully",
          state: true,
        })
        navigate(-1);
      })
      .catch((err) => {
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: false,
        })      

      })
  };

  return (
    <div className={styles.manualUploadContainer}>
      <div className={styles.manualUploadHeader}>
        <div onClick={()=>{navigate(-1)}}>
          <BackIcon/>
        <p>Edit User</p>
</div>
      </div>

      <form className={styles.manualForm}>
        <div className={styles.gridRow}>
          <div className={styles.box}>
            <label htmlFor="username" className={styles.Important}>
              User Name <span style={{ color: "red" }}>*</span>
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter Username"
            />
          </div>

          <div className={styles.box}>
            <label htmlFor="emp_id" className={styles.Important}>
              Employee ID<span style={{ color: "red" }}>*</span>
            </label>
            <input
              type="text"
              id="emp_id"
              name="emp_id"
              value={formData.emp_id}
              onChange={handleChange}
              placeholder="Enter Employee Id"
              readOnly
            />
          </div>
        </div>

        <div className={styles.box}>
          <label htmlFor="email" className={styles.Important}>
            Email Address <span style={{ color: "red" }}>*</span>
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter Email Address"
          />
        </div>

        {/* <div className={styles.box}>
          <label htmlFor="password">
            Password<span style={{ color: "red" }}>*</span>
          </label>
          <input
            className={(formData.password.length<8&&formData.password.length>0)
              ?styles.deniedInput
              :(formData.password.length>7)
              ?styles.accessInput:""}
            type="text"
            id="password"
            name="password"
            readOnly
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter Password"
          />
        </div> */}
        <div className={styles.gridRow}>
          {/* <div className={styles.box}>
            <label htmlFor="assigneeEmpId">
              Assignee Emp ID
              <span className={styles.IIcon} onClick={()=>{setToogleInfo(!toogleInfo)}}>
                <IIcon />
              </span>
            </label>
            {toogleInfo && <span className={styles.IIconInfo}>
              The employee Id of the Assignee will be shown here.
            </span>}
            <input
              type="text"
              id="assigneeEmpId"
              name="assigneeEmpId"
              value={formData.assigneeEmpId}
              onChange={handleChange}
              placeholder="Enter assigneeEmpId"
            />
          </div> */}

          <div className={styles.box}>
            <label>
              Status<span style={{ color: "red" }}>*</span>
            </label>
            <div className={styles.radioGroup}>
              <div className={styles.radioOption}>
                <input
                  type="radio"
                  name="is_active"
                  id="is_active"
                  value="true"
                  checked={formData.is_active === true}
                  onChange={handleChange}
                />
                <label htmlFor="is_active" className={styles.radioLabel}>
                  Active
                </label>
              </div>

              <div className={styles.radioOption}>
                <input
                  type="radio"
                  name="is_active"
                  id="is_inactive"
                  value="false"
                  checked={formData.is_active === false}
                  onChange={handleChange}
                />
                <label htmlFor="is_inactive" className={styles.radioLabel}>
                  Inactive
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className={styles.buttonGroup}>
          <button
            type="button"
            className={styles.cancelButton}
            onClick={(e) => {
              handleSubmit(e)
            }}
          >
            Save
          </button>
        </div>
      </form>
    </div>
  );
}
