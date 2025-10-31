import { useState } from "react";
import styles from "./Manual.module.css";
import IIcon from "../../../Icons/IIcon";
import { useNavigate } from "react-router-dom";
import axios from "../../../service";
import { useLOIData, useUserPopupStore } from "../../../store";
import { UpdateTimeline } from "../../Timeline/UpdateTImeLine";
import { TimeLineRoute } from "../../../RouteHelper/TimeLineRoute";
import { setSessionStorage } from "../../../sessionHelper";


export default function Manual() {
  const { message, setMessage } = useUserPopupStore();
  const navigate = useNavigate();
  let { selectedData, setSelectedData } = useLOIData();
  const [toogleInfo, setToogleInfo] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    emp_id: "",
    email: "",
    password: "",
    // assigneeEmpId: "",
    is_active: true,
    role: "user",
  });

  const isFormValid =
  formData.username.trim() !== "" &&
  formData.emp_id.trim() !== "" &&
  formData.email.trim() !== "" &&
  formData.password.trim() !== "" &&
  formData.password.length > 7;

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
    let company_id = JSON.parse(localStorage.getItem("user"))?.company_id;

    axios
      .post("/auth/users", [{company_id:company_id,...formData}])
      .then((res) => {
        // localStorage.setItem("createdUser", res.data[0].id);
        sessionStorage.setItem("createdUser", res.data[0].id)
        setMessage({
          enable: true,
          msg: "User Created Successfully",
          state: true,
        })

        if (type == "save") {
          localStorage.setItem("currentPathLocation","Create User");
          navigate(-1);
        } else {
          localStorage.setItem("TLData",JSON.stringify(TimeLineRoute["/migoto-cms/createUser/assignCourse/:id"]))
          navigate(`/migoto-cms/createUser/assignCourse/${res.data[0].id}`);
          localStorage.setItem("currentPathLocation","Assign Course");
          // setPathLocation("Assign Course");
          setSelectedData("createdUser",[res.data[0].id]);
          setSessionStorage("createdUser",[res.data[0].id])
          UpdateTimeline(1, {
            status: "success",
            description: `User Created`
          },setSelectedData);
          UpdateTimeline("Course Selection", {
            status: "warning",
            description: `In Progress`
          },setSelectedData);
        }
      })
      .catch((err) => {
        console.log("err: ", err);
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
        <p>Manual Upload</p>
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

        <div className={styles.box}>
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
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter Password"
          />
        </div>

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
                  value={true}
                  id="is_active"
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
                  value={false}
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
            disabled={!isFormValid}
            onClick={(e) => {
              handleSubmit(e, "save");
            }}
          >
            Save
          </button>
          <button
            type="button"
            className={styles.submitButton}
            disabled={!isFormValid}
            onClick={(e) => {
              handleSubmit(e, "assign");
            }}
          >
            Save & Assign Course
          </button>
        </div>
      </form>
    </div>
  );
}
