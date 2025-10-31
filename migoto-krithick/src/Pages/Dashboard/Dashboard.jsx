import React, { useState, useEffect } from "react";
import styles from '../Dashboard/Dashboard.module.css';
import UserStatusCard from "./UserStatus/UserStatusCard";
import PlayIcon from "../../Icons/PlayIcon";
import Chart from "./Chart/Chart";
import CTable from "./Table/CTable";
import axios from "../../service";

// import { usePathLocation } from '../../store'
function Dashboard() {
  // let {pathLocation, setPathLocation} = usePathLocation()
  const [userStats, setUserStats] = useState({
    total_users: 0,
    active_users: 0,
    assigned_users: 0,
    unassigned_users: 0,
  });

  useEffect(() => {
    // setPathLocation("Dashboard");
    localStorage.setItem("currentPathLocation","Dashboard")
    const fetchStats = async () => {
      try {
        const response = await axios.get("/dashboard/user-stats");
        setUserStats(response.data);
      } catch (error) {
        console.error("Error fetching user stats:", error);
      }
    };

    fetchStats();
  }, []);
  return (
    <>
      <div className={styles.mainContainer}>
        <div className={styles.leftContainer}>
          <div className={styles.userStatus}>
            <span className={styles.uHeader}>User Status</span>
            <div className={styles.statusContainer}>
              <UserStatusCard
                title="Overall"
                number={userStats.total_users}
                icon={1}
                numberColor="#005B84"
                iconBgColor="#005B8433"
              />
              <UserStatusCard
                title="Assigned Users"
                number={userStats.assigned_users}
                icon={2}
                numberColor="#1890ff"
                iconBgColor="#69c0ff"
              />
              <UserStatusCard
                title="Un assigned Users"
                number={userStats.unassigned_users}
                icon={3}
                numberColor="#E13300"
                iconBgColor="#FADBD2"
              />
              <UserStatusCard
                title="Active Users"
                number={userStats.active_users}
                icon={4}
                numberColor="#00841E"
                iconBgColor="#00841E33"
              />
            </div>
          </div>{" "}
          <div className={styles.tableContainer}>
            <span className={styles.uHeader}>Highly Ranked Sessions</span>
            <CTable />{" "}
          </div>
        </div>
        <div className={styles.rightContainer}>
          <span className={styles.uHeader}>Course Status</span>

          <Chart />
        </div>
      </div>
    </>
  );
}

export default Dashboard;