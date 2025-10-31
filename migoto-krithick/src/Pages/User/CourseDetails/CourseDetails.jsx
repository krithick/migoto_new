
import React, { useEffect, useRef, useState } from "react";
import EditIcon from "../../../Icons/EditIcon";
import BackIcon from "../../../Icons/BackIcon";
import styles from "./CourseDetails.module.css";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useLOIData, useReportStore } from "../../../store";
import axios from "../../../service";
import Card from "../../../Components/Card/Card";
import UserDetailSideBar from "../../../Components/UserDetailBox/UserDetailSideBar";


function CourseDetails({val,Swap}) {
  const [selectedModule, setSelectedModule] = useState(null);
  const [selectedScenarios, setSelectedScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [page, setPage] = useState("In Progress Courses");
  const { selectedData, setSelectedData, setClean } = useLOIData();
  let [currentPage, setCurrentPage] = useState("moduleLists");
  const [title, setTitle] = useState("Title")
  const [header, setHeader] = useState("courseHeader")

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
    // console.log("selectedData.length: ", Object.keys(selectedData).length);
    if (currentPage === "sessions") {
      setPage("Sessions");
      fetchCourses(
        `auth/admin/users/${id}/scenario-sessions?scenario_id=${selectedData["sessions"]}&mode=assess_mode`, //for chat lists
        "scenarios_sessions",
        setHeader("scenarioHeader")
      )
    }else if(selectedData["assignedCourse"] && selectedData["moduleLists"]){
      fetchCourses(`/scenario-assignments/user/${val?.id}/module/${selectedData["moduleLists"]}`, // for showing assigned scenario in the module 
        "scenarios");
      setCurrentPage("sessions");
      setHeader("moduleHeader")
    }else if(selectedData["assignedCourse"]){
      // fetchCourses(`/courses/${selectedData["assignedCourse"]}/full`, "modules");
      fetchCourses(`/module-assignments/user/${val?.id}/course/${selectedData["assignedCourse"]}`,  //for showing assigned modules in the course
         "modules");
         setHeader("courseHeader")
    }
  }, [selectedData]);

  useEffect(()=>{
    setData(data)
  },[selectedData])



  function handleClick(targetPage) {
    if (targetPage === "In Progress Courses") {
      setSelectedModule(null);
      setSelectedScenarios([]);
      setSelectedScenario(null);
      setClean()
      setSelectedData("assignedCourse",null)
    }
    setPage(targetPage);
  }


  function getDateFromISOString(isoString) {
    const date = new Date(isoString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0"); // months are 0-indexed
    const day = String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
  }
  
  return (
    <div className={styles.tab}>
        <UserDetailSideBar val={val} Swap={()=>Swap()} />
        <div className={styles.mainBox}>
        <div className={styles.mainHeader}>
          <div className={styles.HeaderBoxy}>
            {page == "In Progress Courses" && (
              <BackIcon onClick={() => handleClick("In Progress Courses")} />
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
              
              {header=="courseHeader" && (<img src={selectedData[header]?.thumbnail_url} alt="Avt" />)}
                {header!="courseHeader" && (<img src={selectedData[header]?.info?.thumbnail_url} alt="Avt" />)}
            </div>

            <div className={styles.courseTileSub2}>
              <div className={styles.subTitle}>
                Title
              </div>
              <div className={styles.subValue} title={selectedData[header]?.title}>

                {header=="courseHeader" && (selectedData[header]?.title?.length > 30 ? selectedData[header].title?.slice(0, 30)?.replaceAll(/[_-]/g, " ") + "..." : selectedData[header]?.title?.replaceAll(/[_-]/g, " "))}
                {header!="courseHeader" && (selectedData[header]?.info?.title?.length > 30 ? selectedData[header]?.info?.title?.slice(0, 30)?.replaceAll(/[_-]/g, " ") + "..." : selectedData[header]?.info?.title?.replaceAll(/[_-]/g, " "))}
              </div>
            </div>

            <div className={styles.courseTileSub3}>
              <div className={styles.subTitle}>
              Assigned At
              </div>
              <div className={styles.subValue}>
              {(selectedData[header]?.assigned_date?.slice(0,10)?.trim())}

              </div>
            </div>

            <div className={styles.courseTileSub4}>
              <div className={styles.subTitle}>
                {selectedScenario
                  ? "Scenario Status"
                  : selectedModule
                  ? "Module Status"
                  : "Course Status"}
              </div>
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
                  {selectedData["moduleLists"]
                    ? "List Of Scenarios Assigned"
                    : "List Of Modules Assigned"}
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
                    {selectedModule ? "Assign Course" : "Assign Course"}
                  </div>
                </div>
              )}
            </div>}
            <div className={styles.detailBoxMain}>
              {(data && page != "Sessions") &&
                Object.keys(selectedData).length !== 3 &&
                data.map((item, index) => {
                  // console.log('item: ', item,currentPage);
                  return (
                    <Card data={item} key={index} currentPage={currentPage} />
                  );
                })}
              {data && page == "Sessions" && (
                <table>
                  <thead>
                    <tr>
                      <td>S.no</td>
                      <td>Scenario Title</td>
                      <td>Attempted Date</td>
                      <td></td>
                    </tr>
                  </thead>
                  <tbody>
                    {/* {selectedScenario ? ( */}
                    <>
                      {data.map((v, i) => (
                        <>
                          <tr>
                            <td>{i + 1}</td>
                            <td>{v.scenario_name}</td>
                            <td>
                              {getDateFromISOString(v.session_last_updated)}
                            </td>
                            <td
                              className={styles.report}
                              onClick={() =>
                                setReport({ state: true, id: v?.session_id })
                              }
                            >
                              View Report
                            </td>
                          </tr>
                        </>
                      ))}
                     
                      {/* <tr>
                          <td>5</td>
                          <td>Completed Date</td>
                          <td>{data.completedDate}</td>
                        </tr>
                        <tr>
                          <td>6</td>
                          <td>Description</td>
                          <td>{selectedScenario.description}</td>
                        </tr> */}
                    </>
                    {/* ) : (
                      currentList.map((item, index) => (
                        <tr key={`${index}-row`}>
                          <td>{index + 1}</td>
                          <td>{item.title}</td>
                          {selectedModule ? (
                            <>
                              <td>{item.assignedDate}</td>
                              <td className={styles.statusItem}>
                                {item.status}
                              </td>
                              <td>{item.completedDate}</td>
                              <td
                                onClick={() => {
                                  setSelectedScenario(item);
                                }}
                              >
                                <div className={styles.viewDetail}>
                                  <div>View Detail</div>
                                  <div>svg</div>
                                </div>
                              </td>
                            </>
                          ) : (
                            <>
                              <td>{item.assigned}</td>
                              <td>{item.status}</td>
                              <td>{item.Assigneddate}</td>
                              <td>{item.Completeddate}</td>
                              <td
                                onClick={() => {
                                  setSelectedModule(item);
                                  setSelectedScenarios(scenarioData);
                                  handleClick(item.title);
                                }}
                              >
                                <div className={styles.viewDetail}>
                                  <div>View Detail</div>
                                  <div>svg</div>
                                </div>
                              </td>
                            </>
                          )}
                        </tr>
                      ))
                    )} */}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CourseDetails;
