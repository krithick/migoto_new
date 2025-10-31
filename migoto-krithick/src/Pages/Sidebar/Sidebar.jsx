import React, { useEffect, useRef, useState } from "react";
import styles from "./Sidebar.module.css";
import { useNavigate } from "react-router-dom";
import DashboardIcon from "../../Icons/DashboardIcon";
import UsersDashIcon from "../../Icons/UsersDashIcon";
import CourseDashIcon from "../../Icons/CourseDashIcon";
import AvatarDashIcon from "../../Icons/AvatarDashIcon";
import AccountDashIcon from "../../Icons/AccountDashIcon";
import HelpDashIcon from "../../Icons/HelpDashIcon";
import LogoutDashIcon from "../../Icons/LogoutDashIcon";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../store";
import { Navcontent } from "./SidebarPopUpContent";
import { clearAllData, clearCourseData, clearScenarioData } from "../../sessionHelper";

function Sidebar() {
  let navigate = useNavigate();
  let activeTab = localStorage.getItem("activeTab");
    const {isPreview, setIsPreview} = usePreviewStore();
    const {selectedData, setSelectedData} = useLOIData();
  const [active, setActive] = useState(
    activeTab === null ? "dashboard" : activeTab
  );
  // const menuContainerRef = useRef(null);
  // const activeIndicatorRef = useRef(null);

  useEffect(()=>{
    // console.log("activeTab",activeTab);
    if(window.location.pathname=="/migoto-cms/dashboard"){
      setActive("dashboard");
    }
    if(active!="course"){
      setSelectedData("showModule",null)
      setSelectedData("showScenario",null)
      setSelectedData("showCourse",null)
      setSelectedData("moduleId",null)
      setSelectedData("courseId",null)
    }
    if(activeTab=="users"){
      setActive("users");
    }
    // updateActiveIndicator(active);

  },[activeTab])

  
//   const updateActiveIndicator = (activeId) => {
//   const activeElement = document.querySelector(`[data-nav="${activeId}"]`);
//   const indicator = activeIndicatorRef.current;
  
//   if (activeElement && indicator) {
//     const rect = activeElement.getBoundingClientRect();
//     const containerRect = menuContainerRef.current.getBoundingClientRect();
    
//     const offsetTop = rect.top - containerRect.top;
    
//     indicator.style.transform = `translateY(${offsetTop}px)`;
//     indicator.style.opacity = '1';
//   }
// };

const checkNavigation = async(currentPath, navTo) => {
  //true leads to mavigate
  //false leads to stay same
    if(navTo == "dashboard"){
      if(currentPath=="/migoto-cms/dashboard"){
        return true
      }
      if(currentPath=="/migoto-cms/users"||
        currentPath=="/migoto-cms/admins" ||
        currentPath=="/migoto-cms/courseManagement"){
        return true;
      }else{
        return new Promise((resolve) => {
          setIsPreview({
            enable: true,
            msg: `${Navcontent[currentPath]?Navcontent[currentPath]:"Are you sure you want to proceed with this action?"}`,
            value: "ok/cancel",
            resolve,
          });
        });
      }
    }else if(navTo == "adminManagement"){
      if(currentPath=="/migoto-cms/admins"){
        return true
      }
      if(currentPath=="/migoto-cms/dashboard"||
        currentPath=="/migoto-cms/admins" ||
        currentPath=="/migoto-cms/users" ||
        currentPath=="/migoto-cms/courseManagement"){
        return true;
      }else{
        return new Promise((resolve) => {
          setIsPreview({
            enable: true,
            msg: `${Navcontent[currentPath]?Navcontent[currentPath]:"Are you sure you want to proceed with this action?"}`,
            value: "ok/cancel",
            resolve,
          });
        });
      }
    }else if(navTo == "users"){
      if(currentPath=="/migoto-cms/users"){
        return true
      }
      if(currentPath=="/migoto-cms/dashboard"||
        currentPath=="/migoto-cms/admins" ||
        currentPath=="/migoto-cms/courseManagement"){
        return true;
      }else{
        return new Promise((resolve) => {
          setIsPreview({
            enable: true,
            msg: `${Navcontent[currentPath]?Navcontent[currentPath]:"Are you sure you want to proceed with this action?"}`,
            value: "ok/cancel",
            resolve,
          });
        });
      }
    }else if(navTo == "course"){
      if(currentPath == "/migoto-cms/courseManagement"){
        return true
      }
      if(currentPath=="/migoto-cms/dashboard"||
        currentPath=="/migoto-cms/admins" ||
        currentPath=="/migoto-cms/users"){
        return true;
      }else{
        return new Promise((resolve) => {
          setIsPreview({
            enable: true,
            msg: `${Navcontent[currentPath]?Navcontent[currentPath]:"Are you sure you want to proceed with this action?"}`,
            value: "ok/cancel",
            resolve,
          });
        });
      }
    }
}

const clearData = () =>{
  setSelectedData("List Of Modules",null)
  setSelectedData("List Of Courses",null)
  setSelectedData("List Of Scenarios",null)
  setSelectedData("showModule",null)
  setSelectedData("showScenario",null)
  setSelectedData("showCourse",null)
  setSelectedData("moduleId",null)
  setSelectedData("courseId",null)
  setSelectedData("assignedCourse",null)
  setSelectedData("sessions",null)
  setSelectedData("moduleLists",null)
  setSelectedData("moduleHeader",null)
  setSelectedData("scenarioHeader",null)
  setSelectedData("courseHeader",null)
  // sessionStorage.removeItem("showModule");
  // sessionStorage.removeItem("showScenario");
  // sessionStorage.removeItem("showCourse");
  // sessionStorage.removeItem("moduleId");
  // sessionStorage.removeItem("courseId");
}

const handleNavigation=async(nav)=>{
  let allow = await checkNavigation(window.location.pathname, nav)
  if(allow){
    if(nav=="dashboard"){
      localStorage.setItem("activeTab", "dashboard");
      localStorage.setItem("timeLine", JSON.stringify(false));
      setActive("dashboard");
      navigate("/migoto-cms/dashboard");
      localStorage.setItem("currentPathLocation", "Dashboard")
      localStorage.setItem("flow", `Dashboard flow`);
      clearAllData()
      clearCourseData()
    }else if(nav=="adminManagement"){
      localStorage.setItem("activeTab", "adminManagement");
      localStorage.setItem("timeLine", JSON.stringify(false));
      setActive("adminManagement");
      navigate("/migoto-cms/admins");
      localStorage.setItem("currentPathLocation", "Admin Management")
      localStorage.setItem("flow", `adminManagement flow`);
    }else if(nav=="users"){
      localStorage.setItem("activeTab", "users");
      localStorage.setItem("timeLine", JSON.stringify(false));
      setActive("users");
      navigate("/migoto-cms/users");
      setSelectedData("moduleLists",null)
      setSelectedData("sessions",null)
      setSelectedData("assignedCourse",null)
      localStorage.setItem("currentPathLocation", "User")
      localStorage.setItem("flow", `UserManagement flow`);
      clearAllData()
      clearCourseData()
    }else if(nav=="course"){
      localStorage.setItem("timeLine", JSON.stringify(false));
      setSelectedData("showModule",null)
      setSelectedData("showCourse",null)
      setSelectedData("showScenario",null)
      navigate('/migoto-cms/courseManagement'),
      setActive("course"),
      localStorage.setItem("activeTab", "course"),
      localStorage.setItem("currentPathLocation", "Course Management")
      localStorage.setItem("flow", `CourseManagement flow`);
      clearAllData()
      clearCourseData()
    }else if(nav=="avatar"){
      localStorage.setItem("timeLine", JSON.stringify(false));
      navigate('/migoto-cms/avatarManagement'),
      localStorage.setItem("activeTab", "avatar"),
      setActive("avatar"),
      localStorage.setItem("currentPathLocation", "Avatar Management")
      localStorage.setItem("flow", `Avatar flow`);
    }
    clearData()
  }
  // clearData()
}

  return (
    <>
      <div className={styles.sidebar}>
        <div className={styles.logoContainer}>
          <img className={styles.logoImg} src="/Logo.png" alt="" />
        </div>
        {/* <div ref={menuContainerRef} className={styles.menuContainer}> */}
        <div className={styles.menuContainer}>
        {/* <div ref={activeIndicatorRef} className={styles.activeIndicator}/> */}
           <div className={styles.menuTop}>
            <span className={`${active === "dashboard" ? styles.active : ""} ${styles.sidebarNav}`}
              onClick={() => {handleNavigation("dashboard")}}
            >
              <p className={styles.navTitle}>
                <DashboardIcon className={styles.dashIcon} />
                Dashboard
              </p>
            </span>
            {/* ---------------Admin----------------------- */}
            {localStorage.getItem("role")=="superadmin"&&<span className={`${active === "adminManagement" ? styles.active : ""} ${styles.sidebarNav}`}
              onClick={() => {handleNavigation("adminManagement")}}>
              <p className={styles.navTitle}>
                <UsersDashIcon />
                Admin Management
              </p>
            </span>}
            {/* ---------------User----------------------- */}
            <span className={`${active === "users" ? styles.active : ""} ${styles.sidebarNav}`}
              onClick={() => {handleNavigation("users")}}
            >
              <p className={styles.navTitle}>
                <UsersDashIcon />
                User Management
              </p>
            </span>
            <span className={`${active === "course" ? styles.active : ""} ${styles.sidebarNav}`}
              onClick={()=>{handleNavigation("course")}}
            >
              <p className={styles.navTitle}>
                <CourseDashIcon />
                Course Management
              </p>
            </span>
            {/* <spanclassName={`${active === "avatar" ? styles.active : ""} ${styles.sidebarNav}`}
              onClick={()=>{handleNavigation("avatar")}}
            >
              <p className={styles.navTitle} >
              <AvatarDashIcon />
                Avatar
              </p>
            </span> */}
          </div>

          <div className={styles.menuBottom}>
            <span className={styles.sidebarNav}>
              <p className={styles.navTitle}>
                <AccountDashIcon />
                Account Preference
              </p>
            </span>
            <span className={styles.sidebarNav}>
              <p className={styles.navTitle}>
                <HelpDashIcon />
                Help
              </p>
            </span>
            <span
              className={styles.sidebarNav}
              onClick={() => {
                navigate("/migoto-cms");
                localStorage.clear();
                location.reload();
              }}
            >
              <p className={styles.navTitle}>
                <LogoutDashIcon className={styles.logoutIcon} />
                Logout
              </p>
            </span>
          </div>
        </div>
      </div>
    </>
  );
}

export default Sidebar;
