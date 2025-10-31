import React, { useEffect, useRef, useState } from "react";
import EditIcon from "../../../Icons/EditIcon";
import BackIcon from "../../../Icons/BackIcon";
import styles from "./UserCourse.module.css";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useLOIData, useReportStore } from "../../../store";
import axios from "../../../service";
import Card from "../../../Components/Card/Card";
import UserDetailSideBar from "../../../Components/UserDetailBox/UserDetailSideBar";
import { getSessionStorage, setSessionStorage } from "../../../sessionHelper";
import { Button } from "antd";


function UserScenario({val,Swap}) {
  const [selectedModule, setSelectedModule] = useState(null);
  const [selectedScenarios, setSelectedScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [page, setPage] = useState("In Progress Courses");
  const { selectedData, setSelectedData, setClean } = useLOIData();
  let [currentPage, setCurrentPage] = useState("sessions");
  const [title, setTitle] = useState("Title")
  const [header, setHeader] = useState("moduleHeader")

  let { setReport } = useReportStore();

  let navigate = useNavigate();
  let { id } = useParams();
  const [data, setData] = useState();
  const fetchCourses = async (url1, type,position) => {
    try {
      const userList = await axios.get(url1);
      setData(userList.data);

      if (type == "scenarios_sessions") {
        let data = userList.data;
        setData(data);
      } else {
        let data = userList.data;
        setData(data);
        setTitle(userList.data)
      }
    } catch (e) {
      console.log("Unable to fetch users", e);
    }
  };
  

  useEffect(() => {
      fetchCourses(`/scenario-assignments/user/${id}/module/${getSessionStorage("moduleLists")}`, // for showing assigned scenario in the module 
        "scenarios");
        localStorage.setItem("currentPathLocation","User")

  }, []);


  function getDateFromISOString(isoString) {
    const date = new Date(isoString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0"); // months are 0-indexed
    const day = String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
  }

  const handleNextPage = () => {
    if(selectedData["sessions"]?.length>0){
        setSessionStorage("sessions",selectedData["sessions"])    
        setSessionStorage("scenarioHeader",selectedData["scenarioHeader"])    
        let path = window.location.pathname.replace("scenario","chats")
        navigate(path)
    }
  }
  const handlePrevious = () => {
    let path = window.location.pathname.replace("scenario","module")
    navigate(path)
  }


  
  return (
    <div className={styles.tab}>
        <UserDetailSideBar val={getSessionStorage("userData")} Swap={()=>Swap()} />
        <div className={styles.mainBox}>
        <div className={styles.mainHeader}>
          <div className={styles.HeaderBoxy}>
            {page == "In Progress Courses" && (
              <BackIcon onClick={() => handlePrevious()} />
            )}
            {/* {page != "In Progress Courses" && (
              <BackIcon onClick={() => {setPage("Sessions"),setSelectedData("scenarioHeader",null),setSelectedData("sessions",null),setCurrentPage("sessions")}} />
            )} */}
            <p>{page}</p>
          </div>
        </div>

        <div className={styles.mainSection}>
         {<div className={styles.courseTile}>
            <div className={styles.courseTileSub1}>
              
              {header=="courseHeader" && (<img src={getSessionStorage(header)?.thumbnail_url} alt="Avt" />)}
                {header!="courseHeader" && (<img src={getSessionStorage(header)?.info?.thumbnail_url} alt="Avt" />)}
            </div>

            <div className={styles.courseTileSub2}>
              <div className={styles.subTitle}>
                Title
              </div>
              <div className={styles.subValue} title={getSessionStorage(header)?.title}>

                {header=="courseHeader" && (getSessionStorage(header)?.title?.length > 30 ?getSessionStorage(header).title?.slice(0, 30)?.replaceAll(/[_-]/g, " ") + "..." : selectedData[header]?.title?.replaceAll(/[_-]/g, " "))}
                {header!="courseHeader" && (getSessionStorage(header)?.info?.title?.length > 30 ?getSessionStorage(header)?.info?.title?.slice(0, 30)?.replaceAll(/[_-]/g, " ") + "..." : selectedData[header]?.info?.title?.replaceAll(/[_-]/g, " "))}
              </div>
            </div>

            <div className={styles.courseTileSub3}>
              <div className={styles.subTitle}>
              Assigned At
              </div>
              <div className={styles.subValue}>
              {(getSessionStorage(header)?.assigned_date?.slice(0,10)?.trim())}

              </div>
            </div>

            <div className={styles.courseTileSub4}>
              <div className={styles.subTitle}>
                  Course Status</div>
              <div className={styles.subValue4}>
                {selectedScenario?.status ||
                  selectedModule?.status ||
                  "In Progress"}
              </div>
            </div>
          </div>}

          <div className={styles.detailBox}>
          {page != "Sessions" &&<div className={styles.detailBoxHeader}>
              <div className={styles.dbHeaderLeft}>
                <div className={styles.headerLeftTitle}>
                    List Of Scenarios Assigned
                </div>
              </div>
              {!selectedScenario &&  (
                <div className={styles.dbHeaderRight}>
                  <div
                    className={styles.assignBtn}
                    onClick={() => {
                      navigate(`assignCourse/${id}`);
                    }}
                  >
                    Assign Course
                  </div>
                </div>
              )}
            </div>}
            <div className={styles.detailBoxMain}>
              {
                data?.map((item, index) => {
                  return (
                    <Card data={item} key={index} currentPage={currentPage} />
                  );
                })}
            </div>
          </div>
          <div className={styles.footer}>
                <Button className={styles.cancelBtn}
                  onClick={() => {
                    handlePrevious()
                  }}>{"< Back"}</Button>
                {<Button className={styles.primaryBtn}type="primary"
                  onClick={() => {
                    handleNextPage()
                  }}>{"Next >"}</Button>}
              </div>


        </div>
      </div>
    </div>
  );
}

export default UserScenario;
