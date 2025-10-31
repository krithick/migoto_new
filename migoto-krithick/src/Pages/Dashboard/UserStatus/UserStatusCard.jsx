import React from "react";
import { Card, Typography } from "antd";
import {
  ArrowRightOutlined,
  UserAddOutlined,
  UserDeleteOutlined,
  UsergroupAddOutlined,
  UsergroupDeleteOutlined,
  UserOutlined,
} from "@ant-design/icons";
import styles from "./UserStatusCard.module.css";
import UsersIcon from "../../../Icons/UsersIcon";
import { useNavigate } from "react-router-dom";
import { useLOIData } from "../../../store";

const { Text, Title } = Typography;

const UserStatusCard = ({ title, number, icon, numberColor, iconBgColor }) => {
  let navigate = useNavigate()
      const {selectedData, setSelectedData} = useLOIData();
  
  return (
    <>
      <Card
        className={styles.cardContainer}
        // className={styles.cardContainer1}
      >
        <div className={styles.cardHeader}>
          <Text className={styles.cardTitle}>{title}</Text>
          <div
            className={styles.iconContainer}
            style={{ backgroundColor: iconBgColor }}
          >
            {icon === 1 && (
              <UserOutlined
                style={{ color: numberColor }}
                className={styles.userIcon}
              />
            )}
            {icon === 2 && (
              <UsergroupAddOutlined
                style={{ color: "#006cd2" }}
                className={styles.userIcon}
              />
            )}
            {icon === 3 && (
              <UsergroupDeleteOutlined
                style={{ color: numberColor }}
                className={styles.userIcon}
              />
            )}

            {icon === 4 && (
              <UserAddOutlined
                style={{ color: numberColor }}
                className={styles.userIcon}
              />
            )}
            {/* You could conditionally render Icon here if needed */}
            {/* <Icon style={{ color: "#fff", fontSize: "14px" }} /> */}
          </div>
        </div>
        <span
          level={2}
          className={styles.numberTitle}
          style={{ color: numberColor }}
        >
          {number}
          <div className={styles.viewDetail} onClick={()=>{
                  localStorage.setItem("activeTab", "users");
                  navigate("/migoto-cms/users");
                  setSelectedData("moduleLists",null)
                  setSelectedData("sessions",null)
                  setSelectedData("assignedCourse",null)
                  localStorage.setItem("currentPathLocation", "User")
                  localStorage.setItem("flow", `UserManagement flow`);
            
          }}>
            <Text className={styles.viewText}>View Detail</Text>
            <ArrowRightOutlined className={styles.arrowIcon} />
          </div>
        </span>
      </Card>
    </>
  );
};

export default UserStatusCard;
