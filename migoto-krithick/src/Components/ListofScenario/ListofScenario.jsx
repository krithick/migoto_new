import React, { useEffect, useState } from "react";
import styles from "../ListofScenario/ListofScenario.module.css";
import { useLOIData, useModeData, useUserPopupStore } from "../../store.js";
import axios from "../../service";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import SearchIcon from "../../Icons/SearchIcon.jsx";
import CreateCourseIcon from "../../Icons/CreateCourseIcon.jsx";
import ListofMode from "../../Pages/ListofItems/ListofMode.jsx";
import FilterIcon from "../../Icons/FilterIcon.jsx";
import Card from "../Card/Card.jsx";
import { UpdateTimeline } from "../Timeline/UpdateTImeLine.js";
import { getSessionStorage, setSessionStorage } from "../../sessionHelper.js";

function ListofScenario() {
  const location = useLocation();
  const { selectedData, setSelectedData } = useLOIData();
  let [activeCourse, setActiveCourse] = useState("all");
  let [currentPage, setCurrentPage] = useState(location.state?.myData?location.state?.myData:"List Of Courses");
  let [filterOn, setFilterOn] = useState(false);
  let [filterData, setFilterData] = useState("");
  let [search, setSearch] = useState("");
  let [datas, setDatas] = useState();
  let [data, setData] = useState();
  let userEmpId = JSON.parse(localStorage.getItem("user"));
  const navigate = useNavigate();
  let flow = useState(localStorage.getItem("flow"));

  //filter based on me ,admin,superadmin along with completed in progress
  const handleChangeCourse = (filter, course) => {
    setActiveCourse(course);
    if (course === "all") {
      if (filterData == "") {
        setData(datas);
      } else {
        setData(datas.filter((item) => item.status === filterData));
      }
    } else if (course === "Me") {
      if (filterData != "") {
        setData(
          datas.filter(
            (item) =>
              item.created_by == userEmpId?.id && item.created_by == filterData
          )
        );
      } else {
        setData(datas.filter((item) => item.created_by == userEmpId?.id));
      }
    } else {
      if (filterData == "") {
        setData(datas.filter((item) => item.creater_role === course));
      } else {
        setData(
          datas.filter(
            (item) => item.creater_role === course && item.status === filterData
          )
        );
      }
    }
  };

  const fetchListOfCourse = () => {
    if (currentPage == "List Of Courses") {
      axios
        .get("/courses/assignable")
        .then((res) => {
          setDatas(res.data);
          setData(res.data);
        })
        .catch((err) => {
          console.log("err: ", err);
          setData([]);
          setDatas([]);
        });
    }
    if (currentPage == "List Of Modules" && getSessionStorage("List Of Courses")) {
      setData([])
      setDatas([])
      axios
        .get(`/courses/${getSessionStorage("List Of Courses")}/modules`)
        .then((res) => {
          setDatas(res.data);
          setData(res.data);
        })
        .catch((err) => {
          console.log("err: ", err);
          setData([]);
          setDatas([]);
        });
    }
    if (currentPage == "List Of Scenario") {
      axios
        .get(`/modules/${getSessionStorage("List Of Modules")}/scenarios`)
        .then((res) => {
          setDatas(res.data);
          setData(res.data);
        })
        .catch((err) => {
          console.log(err);

          setData([]);
          setDatas([]);
        });
    }
  };

  useEffect(() => {
    if (search == "") {
      setData(datas);
    } else {
      setData(
        datas.filter((item) =>
          item?.title?.toLowerCase()?.includes(search?.toLowerCase())
        )
      );
    }
  }, [search]);

  useEffect(() => {
    fetchListOfCourse();
  }, [currentPage]);

  const getAvatarsId = async () => {
    const idList = [
      { key: "LearnModeAvatarInteractionId", setKey: "LearnModeAvatar" },
      { key: "TryModeAvatarInteractionId", setKey: "TryModeAvatar" },
      { key: "AssessModeAvatarInteractionId", setKey: "AssessModeAvatar" },
    ];
  
    const promises = idList.map((element) => 
      axios
        .get(`/avatar-interactions/${getSessionStorage(element.key)}`)
        .then((res) => {
          setSessionStorage(element.setKey, res.data?.avatars);
        })
        .catch((err) => {
          console.log(err);
        })
    );
  
    await Promise.all(promises);
  };

  useEffect(()=>{

      if(location.state?.myData=="List Of Modules"){
        setCurrentPage("List Of Modules");
        setSelectedData("List Of Scenario",null)
        setSelectedData("List Of Scenario",null)
      }
  },[location.state])

  const handleNextPage = async(page, data) => {
    setSessionStorage(page,data)
    if (page == "List Of Courses") {
      setCurrentPage("List Of Modules");
      setActiveCourse("all");
      setFilterData("");
      setFilterOn(false);
      UpdateTimeline("Course Selection", {
        status: "success",
        description: `Selected`
      },setSelectedData);
      UpdateTimeline("Module Selection", {
        status: "warning",
        description: `In Progress`
      },setSelectedData);
    } else if (page == "List Of Modules") {
      setCurrentPage("List Of Scenario");
      setFilterOn(false);
      UpdateTimeline("Module Selection", {
        status: "success",
        description: `Selected`
      },setSelectedData);
      UpdateTimeline("Scenario Selection", {
        status: "warning",
        description: `In Progress`
      },setSelectedData);
    } else {
    //   setCurrentPage("Select Mode");
    //   setFilterOn(false);
    await getAvatarsId()
    // let path = window.location.pathname;
    // const cleanedPath = path?.replace("/avatarSelection", "/personaCreation");
    // navigate(cleanedPath)
    navigate("personaCreation")
    setSelectedData("personaCreated",1)
    UpdateTimeline("Scenario Selection", {
      status: "success",
      description: `Selected`
    },setSelectedData);
    UpdateTimeline(5, {
      status: "warning",
      description: `In Progress`
    },setSelectedData);
    }
    // setCurrentPage("List Of Scenario");
    // setCurrentPage("Select Mode");
  };

  const handlePrevPage = (page) => {
    flow = localStorage.getItem("flow");
    if (flow == "Create Avatar flow" && page == "List Of Courses") {
      let path = window.location.pathname;
      const cleanedPath = path?.replace("/selectScenario", "/dashboard");
      navigate(cleanedPath)
    }
    if (page == "List Of Scenario") {
      setCurrentPage("List Of Modules");
                                UpdateTimeline("Scenario Selection", {
                                  status: "error",
                                  description: ``
                                },setSelectedData);
                                UpdateTimeline("Module Selection", {
                                  status: "warning",
                                  description: `In Progress`
                                },setSelectedData);
    
    } else if (page == "List Of Modules") {
      setCurrentPage("List Of Courses");
      UpdateTimeline("Module Selection", {
        status: "error",
        description: ``
      },setSelectedData);
      UpdateTimeline("Course Selection", {
        status: "warning",
        description: `In Progress`
      },setSelectedData);

    } else {
      setCurrentPage("List Of Scenario");
    }
  };

  useEffect(() => {
    handleChangeCourse(filterData, activeCourse);
  }, [filterData, activeCourse]);


  return (
    <div className={styles.loiContainer}>
      <div className={styles.loiHeader}>
        <div className={styles.loiHeaderLeft}>
          <div className={styles.loiActive}>
            <div>
              <p>{currentPage}</p>
              {currentPage != "Select Mode" && (
                <div
                  onClick={() => {
                    setFilterOn(!filterOn)
                  }}
                  className={styles.filterIcon}
                >
                  <FilterIcon className={styles.filterIcon} />
                </div>
              )}
              {filterOn && (
                <div className={styles.filterList}>
                  <div
                    className={styles.filterData}
                    onClick={() => {
                      setFilterData(""), setFilterOn(false);
                    }}
                  >
                    <span className={styles.blackDot}>路</span>
                    <p>overall</p>
                  </div>
                  <div
                    className={styles.filterData}
                    onClick={() => {
                      setFilterData("Completed"), setFilterOn(false);
                    }}
                  >
                    <span className={styles.greenDot}>路</span>
                    <p>completed</p>
                  </div>
                  <div
                    className={styles.filterData}
                    onClick={() => {
                      setFilterData("In progress"), setFilterOn(false);
                    }}
                  >
                    <span className={styles.yellowDot}>路</span>
                    <p>In progress</p>
                  </div>
                  <div
                    className={styles.filterData}
                    onClick={() => {
                      setFilterData("Yet to assign"), setFilterOn(false);
                    }}
                  >
                    <span className={styles.whiteDot}>路</span>
                    <p>Yet to assign</p>
                  </div>
                </div>
              )}
            </div>
          </div>
          {currentPage == "List Of Courses" && (
            <div className={styles.totalBox}>
              <div
                className={`${styles.box} ${
                  activeCourse === "all" ? styles.active : ""
                }`}
                onClick={() => {
                  handleChangeCourse(filterData, "all");
                }}
              >
                All
              </div>
              <div
                className={`${styles.box} ${
                  activeCourse === "predefined" ? styles.active : ""
                }`}
                onClick={() => {
                  handleChangeCourse(filterData, "predefined");
                }}
              >
                Pre - Defined Courses
              </div>
              <div
                className={`${styles.box} ${
                  activeCourse === "superadmin" ? styles.active : ""
                }`}
                onClick={() => {
                  handleChangeCourse(filterData, "superadmin");
                }}
              >
                Created by Super Admin
              </div>
              <div
                className={`${styles.box} ${
                  activeCourse === "admin" ? styles.active : ""
                }`}
                onClick={() => {
                  handleChangeCourse(filterData, "admin");
                }}
              >
                Created by Admin
              </div>
              <div
                className={`${styles.box} ${
                  activeCourse === "Me" ? styles.active : ""
                }`}
                onClick={() => {
                  handleChangeCourse(filterData, "Me");
                }}
              >
                Created by Me
              </div>
            </div>
          )}
        </div>
        {currentPage != "Select Mode" && (
          <div className={styles.loiHeaderRight}>
            <div className={styles.searchBar}>
              <input
                type="text"
                placeholder="Search Course"
                onChange={(e) => {
                  setSearch(e.target.value);
                }}
              />
              <SearchIcon className={styles.searchIconSvg} />
            </div>

          </div>
        )}
      </div>
      {/* -------------------Body--------------- */}
      <div className={styles.loiBodyOuter}>
        {currentPage != "Select Mode" ? (
          <div className={styles.loiBody}>
            {data?.map((item, index) => {
              return <Card data={item} key={index} currentPage={currentPage} />;
            })}
          </div>
        ) : (
          <ListofMode data={data} />
        )}
      </div>
      <div className={styles.BtnGroup}>
        {currentPage == "List Of Courses" && (
          <button
            className={styles.cancelBtn}
            onClick={() => {
              let path = window.location.pathname;
              const cleanedPath = path?.replace("/selectScenario", "/dashboard");
              navigate(cleanedPath)
            }}
          >
            Cancel
          </button>
        )}
        {currentPage != "List Of Courses" && (
          <button
            className={styles.cancelBtn}
            onClick={() => {
              handlePrevPage(currentPage)
            }}
          >
            {" "}
            {"<"} Back
          </button>
        )}
        {currentPage != "Select Mode" && (
          <button
            className={styles.nextBtn}
            disabled={!selectedData[currentPage]}
            onClick={() => {
              handleNextPage(currentPage, selectedData[currentPage])
            }}>
            Next {">"}
          </button>
        )}
      </div>
    </div>
  );
}

export default ListofScenario;
