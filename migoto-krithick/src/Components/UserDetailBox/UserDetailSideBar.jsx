import React, { useEffect, useRef, useState } from "react";
import styles from '../UserDetailBox/UserDetailSideBar.module.css'
import EditIcon from "../../Icons/EditIcon";
import { useNavigate } from "react-router-dom";
import { useLOIData } from "../../store";
import { getSessionStorage } from "../../sessionHelper";

export default function UserDetailSideBar({val}) {
  const { selectedData } = useLOIData();
  const [userData, setUserData] = useState(val);
  let navigate = useNavigate()

  useEffect(() => {
    setUserData(getSessionStorage("userData"));
  }, [selectedData["userRefresh"]])
  
    let data = {
      name: userData?.data?.username,
      employeeId:userData?.data?.emp_id,
      email: userData?.data?.email,
      create: userData?.data?.created_at?.slice(0,10)?.trim(),
      status: userData?.data?.is_active ? "Active" : "Inactive",
    };
    
  const element = useRef(null);

  useEffect(() => {
    if (element.current) {
      element.current.style.color =
        data.status === "Active" ? "#28A745" : "#E13300";
    }
  }, [data.status]);

  return (
    <div className={styles.sideBar}>
      <div className={styles.sideTop}>
        <div className={styles.editBtn} onClick={()=>{navigate("editUser")}}>
          <div>Edit</div>
          <div>
            <EditIcon />
          </div>
        </div>
        <div className={styles.nameBox}>
        <div>{data?.name?.charAt(0)?.toUpperCase()}</div>
        </div>
      </div>
      <div className={styles.sideContent}>
        <div className={styles.personalInfoBox}>
          <div className={styles.infoTitle}>Personal Information</div>
          <div className={styles.infoStats}>
            <div>User Name</div>
            <div className={styles.statsValue}>{data.name}</div>
          </div>
          <div className={styles.infoStats}>
            <div>Employee ID</div>
            <div className={styles.statsValue}>{data.employeeId}</div>
          </div>
          <div className={styles.infoStats}>
            <div>Email Address</div>
            <div className={styles.statsValue}>{data.email}</div>
          </div>
          <div className={styles.infoStats}>
            <div>Created Date</div>
            <div className={styles.statsValue}>{data.create}</div>
          </div>
          <div className={styles.infoActiveStats}>
            <div>Status</div>
            <div className={styles.statsActiveValue} ref={element}>
              <div className={styles.statsSign}>•</div>
              <div>{data.status}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
