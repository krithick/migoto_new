import React, { useEffect, useRef, useState } from "react";
import styles from "../HeroPage/HeroPage.module.css";
import BackIcon from "../../Icons/BackIcon.jsx";
import CustomTimeline from "../../Components/Timeline/CustomTimeline";
import {useNavigate } from "react-router-dom";
import ReportCard from "../../Components/Report/ReportCard.jsx";
import { Navcontent } from "../Sidebar/SidebarPopUpContent.js";
import Routers from "../../Routers/Routers.jsx";
import {useLoaderStore, useLOIData, usePreviewStore,useReportStore} from "../../store.js";
import CreateButton from "../../Components/HeroPageComponent/CreateButton.jsx";
import HeaderContent from "../../Components/HeroPageComponent/HeaderContent.jsx";
import NavBarComponent from "../../Components/HeroPageComponent/NavBar.jsx";
import TimeLine from "../../Components/Timeline/TimeLine.jsx";
import AILoader from "../../Components/AILoader/AILoader.jsx";
import SelectedData from "../../Components/SelectedDATA/SelectedData.jsx";

function HeroPage() {
  const navigate = useNavigate();
  let { report } = useReportStore();
  const { isPreview, setIsPreview } = usePreviewStore();
  const { selectedData, setSelectedData } = useLOIData();
  const { loaderType } = useLoaderStore();

  //path location is for navbar 
  // let [pathLocation, setPathLocation] = useState(JSON.parse(localStorage.getItem("pathLocation")));

  //currentPathLocation is for which page you are in
  const [currentPathLocation, setCurrentPathLocation] = useState(localStorage.getItem("currentPathLocation"));

  useEffect(() => {
    console.log("selectedData",selectedData);
  }, [selectedData]);

  useEffect(() => {
    const path = window.location.pathname;
    if (path === "/migoto-cms/dashboard" || path === "/migoto-cms/user" || path === "/migoto-cms/courseManagement") {
      localStorage.setItem("timeLine", JSON.stringify(false));
    }
  }, [window.location.pathname]);

  // Check token on every route change
  useEffect(() => {
    const token = localStorage.getItem("migoto-cms-token");
    if (!token) {
      localStorage.clear();
      navigate("/migoto-cms");
    }
  }, [window.location.pathname, navigate]);

  // useEffect(() => {
  //   setPathLocation(JSON.parse(localStorage.getItem("pathLocation")));
  //   if (window.location.pathname == "/migoto-cms/dashboard") {
  //     localStorage.setItem("currentPathLocation", "Dashboard");
  //   }
  //   if (window.location.pathname == "/migoto-cms/users") {
  //     localStorage.setItem("currentPathLocation", "User");
  //   }
  // }, [localStorage.getItem("pathLocation"), window.location.pathname]);

  const checkNavigation = () => {
    let result = new Promise((resolve) => {
      setIsPreview({
        enable: true,
        msg: `${Navcontent[window.location.pathname]?Navcontent[window.location.pathname]:"Are you sure you want to proceed with this action?"}`,
        value: "ok/cancel",
        resolve,
      });
    });
    result.then((res) => {
      if (res) {
          // navigate(-1),
          // setClean(),
          // setSelectedData("assignedCourse", null),
          const currentPath = window.location.pathname;

          if (currentPath.startsWith('/migoto-cms/users')) {
            // Navigate to users if the path starts with /migoto-cms/users
            navigate('/migoto-cms/users');
          } else if (currentPath.startsWith('/migoto-cms/courseManagement')) {
            // Navigate to course management if the path starts with /migoto-cms/courseManagement
            navigate('/migoto-cms/courseManagement');
          } else {
            // Navigate to dashboard for all other paths
            navigate('/migoto-cms/dashboard');
          }
              }
    });
  };
  let checkPath = localStorage.getItem("currentPathLocation");
    
  

  return (
    <>
      <div className={styles.heroPageContainer}>
        <NavBarComponent />
        <div className={styles.contentContainer}>
          <div className={styles.contentContainerHeader}>
            <div className={styles.leftContainer}>
              {/* --------currentPathLocation-------- */}
              <div className={styles.page}>
                {checkPath !== "Course Management" &&
                  checkPath !== "Admin Management" &&
                  checkPath !== "Dashboard" &&
                  checkPath !== "Avatar Management" &&
                  window.location.pathname != "/migoto-cms/users" && (
                    <BackIcon
                      onClick={() => {
                        checkNavigation(window.location.pathname)
                      }}
                    />
                  )}
                <div className={styles.currentPage}>{checkPath}</div>
              </div>
              {/* -----------header content------------ */}
              <HeaderContent />
            </div>
            {/* ------create Btn ---------- */}
            <div className={styles.rightContainer}>
              <CreateButton setCurrentPathLocation={(item)=>setCurrentPathLocation(item)} setPathLocation={(item)=>{setPathLocation(item)}}/>
            </div>
          </div>
          <div className={styles.contentContainerBody}>
          {/* {(loaderType === "mini")&&<AILoader />} */}
            <Routers />
            { JSON.parse(localStorage.getItem("timeLine")) && <TimeLine />}
            {report.state && <ReportCard />}
            {/* <SelectedData /> */}
            {/* <AILoader /> */}
            {/* {userPopup.state && <UserSelect />} */}
          </div>
        </div>
      </div>
    </>
  );
}

export default HeroPage;
