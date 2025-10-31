import React, { useEffect, useState } from "react";
import styles from "../ListofItems/ListofItems.module.css";
import CreateCourseIcon from "../../Icons/CreateCourseIcon";
import SearchIcon from "../../Icons/SearchIcon";
import { useLOIData, useModeData, useUserPopupStore } from "../../store";
import Card from "../../Components/Card/Card";
import FilterIcon from "../../Icons/FilterIcon";
import ListofMode from "./ListofMode";
import axios from "../../service";
import { useNavigate, useParams } from "react-router-dom";
import { UpdateTimeline } from "../../Components/Timeline/UpdateTImeLine";
import { TimeLineRoute } from "../../RouteHelper/TimeLineRoute";
import { setSessionStorage } from "../../sessionHelper";

function ListofItems() {
  const { message, setMessage } = useUserPopupStore();

  const { selectedData, setSelectedData } = useLOIData();
  const { isOpen, setIsOpen } = useModeData();
  let [activeCourse, setActiveCourse] = useState("all");
  let [currentPage, setCurrentPage] = useState("List Of Courses");
  let [filterOn, setFilterOn] = useState(false);
  let [filterData, setFilterData] = useState("");
  let [search, setSearch] = useState("");
  let [datas, setDatas] = useState();
  let [data, setData] = useState();
  let userEmpId = JSON.parse(localStorage.getItem("user"));
  const navigate = useNavigate();
  let [flow, setFlow] = useState(localStorage.getItem("flow"));
  const { id } = useParams();

  const handleCancel = () => {
    if(flow!="UserManagement flow"){
      localStorage.setItem("currentPathLocation", "Create User")
    }
    navigate(-1);
    UpdateTimeline(1, {
      status: "warning",
      description: ``
    },setSelectedData);
    UpdateTimeline("Course Selection", {
      status: "error",
      description: `In Progress`
    },setSelectedData);
  }

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
    if (currentPage == "List Of Modules") {
      axios
        .get(`/courses/${selectedData["List Of Courses"]}/modules`)
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
        .get(`/modules/${selectedData["List Of Modules"]}/scenarios`)
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

  let userId;
  useEffect(() => {
    if (id == "bulkAssign") {
      userId = JSON.parse(sessionStorage.getItem("createdUser"));
      setSelectedData("createdUser", userId);
      // setSessionStorage("createdUser", userId)
    } else {
      userId = [id];
      setSelectedData("createdUser", [id]);
      // setSessionStorage("createdUser", [id])
    }
  }, [id]); //this is for user created and create course

  const assignCourse = async () => {
    let userId;
    if (id == "bulkAssign") {
      userId = JSON.parse(sessionStorage.getItem("createdUser"));
      setSelectedData("createdUser", userId);
      setSessionStorage("createdUser", userId)

    } else {
      userId = [id];
      setSelectedData("createdUser", [id]);
      setSessionStorage("createdUser", [id])

    }

    const courseId = selectedData["List Of Courses"];
    const moduleId = selectedData["List Of Modules"];
    const scenarioId = selectedData["List Of Scenario"];

    const getEnabledModes = () => {
      const modes = [];

      if (isOpen["Learn Mode"]?.enable) modes.push("learn_mode");
      if (isOpen["Try Mode"]?.enable) modes.push("try_mode");
      if (isOpen["Assess Mode"]?.enable) modes.push("assess_mode");

      return modes;
    };

    const payload = {
      user_ids: userId,
      include_all_modules: false,
      include_all_scenarios: false,
      module_ids: [moduleId],
      scenario_mapping: {
        [moduleId]: [scenarioId],
      },
      mode_mapping: {
        [scenarioId]: getEnabledModes(),
      },
    };

    try {
      const response = await axios.post(
        `/course-assignments/course/${courseId}/assign-with-content`,
        payload
      );
      setMessage({
        enable: true,
        msg: "Course Assigned Successfully",
        state: true,
      });

      if (flow == "UserManagement flow") {
        localStorage.setItem("currentPathLocation", "User");
        navigate("/migoto-cms/users");
      } else {
        localStorage.setItem("currentPathLocation", "Dashboard");
        navigate("/migoto-cms/dashboard");
      }
    } catch (error) {
      setMessage({
        enable: true,
        msg: "Something went wrong",
        state: false,
      });

      console.error(
        "Assignment failed:",
        error.response?.data || error.message
      );
    }
  };

  useEffect(() => {
    if (search == "") {
      setData(datas);
    } else {
      setData(
        datas.filter((item) =>
          item.title?.toLowerCase()?.includes(search?.toLowerCase())
        )
      );
    }
  }, [search]);

  useEffect(() => {
    fetchListOfCourse();
  }, [currentPage]);

  const handleNextPage = (page, data) => {
    if (page == "List Of Courses") {
      setCurrentPage("List Of Modules");
      setActiveCourse("all");
      setFilterData("");
      setFilterOn(false);
      UpdateTimeline("Course Selection", {
        status: "success",
        description: `Course Selected`
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
        description: `Module Selected`
      },setSelectedData);
      UpdateTimeline("Scenario Selection", {
        status: "warning",
        description: `In Progress`
      },setSelectedData);
    } else {
      setCurrentPage("Select Mode");
      setFilterOn(false);
      UpdateTimeline("Scenario Selection", {
        status: "success",
        description: `Scenario Selected`
      },setSelectedData);
      UpdateTimeline("Assign Course", {
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
      navigate(-1);
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
      UpdateTimeline("Assign Course", {
        status: "error",
        description: `
        `
      },setSelectedData);
      UpdateTimeline("Scenario Selection", {
        status: "warning",
        description: `In Progress`
      },setSelectedData);

    }
  };

  useEffect(() => {
    handleChangeCourse(filterData, activeCourse);
  }, [filterData, activeCourse]);

  const assignAvatarToCourse = async () => {
    try {
      const res = await axios.get(
        `/scenarios/${selectedData["List Of Scenario"]}/full`
      );
      const response = res.data;

      // Store existing avatar IDs and interaction IDs
      setSelectedData(
        "learnmodeAvatarId",
        response.learn_mode.avatar_interaction.avatars
      );
      setSelectedData(
        "trymodeAvatarId",
        response.try_mode.avatar_interaction.avatars
      );
      setSelectedData(
        "assessmodeAvatarId",
        response.assess_mode.avatar_interaction.avatars
      );
      setSelectedData(
        "learnmodeAvatarInteractionId",
        response.learn_mode.avatar_interaction._id
      );
      setSelectedData(
        "trymodeAvatarInteractionId",
        response.try_mode.avatar_interaction._id
      );
      setSelectedData(
        "assessmodeAvatarInteractionId",
        response.assess_mode.avatar_interaction._id
      );

      // Call PUT
      await putAvatar(response);
    } catch (err) {
      console.log("err: ", err);
    }
  };

  // const putAvatar = async (response) => {
  //   const upcomingAvatarId = selectedData["AvatarCreation"].id;

  //   const modes = ['learn_mode', 'try_mode', 'assess_mode'];

  //   for (const mode of modes) {
  //     const interaction = response[mode]?.avatar_interaction;
  //     const interactionId = interaction?._id;
  //     const prevAvatarIds = interaction?.avatars; // already an array

  //     if (interactionId && prevAvatarIds) {
  //       const payload = {
  //         avatars: [...prevAvatarIds, upcomingAvatarId],
  //       };

  //       console.log(payload,interactionId);

  //       // try {
  //       //   const res = await axios.put(`/avatar-interactions/${interactionId}`, payload);
  //       //   console.log(`${mode} update successful`, res.data);
  //       // } catch (error) {
  //       //   console.error(`Error updating ${mode}:`, error);
  //       // }
  //     }
  //   }
  // };


  const putAvatar = async (response) => {
    const upcomingAvatarId = selectedData["AvatarCreation"].id;

    const modeConfig = [
      { key: "learn_mode", label: "Learn Mode" },
      { key: "try_mode", label: "Try Mode" },
      { key: "assess_mode", label: "Assess Mode" },
    ];

    for (const { key, label } of modeConfig) {
      // Check if mode is enabled
      if (!isOpen[label]?.enable) {
        continue; // Skip this mode if not enabled
      }

      const interaction = response[key]?.avatar_interaction;
      const interactionId = interaction?._id;
      const prevAvatarIds = interaction?.avatars;

      if (interactionId && prevAvatarIds) {
        let parsedPrevAvatars = prevAvatarIds;

        // Fix stringified array issue if needed
        if (
          typeof prevAvatarIds[0] === "string" &&
          prevAvatarIds[0].startsWith("['")
        ) {
          try {
            parsedPrevAvatars = JSON.parse(prevAvatarIds[0]?.replace(/'/g, '"'));
          } catch (e) {
            console.error("Failed to parse prevAvatarIds", e);
            parsedPrevAvatars = [];
          }
        }

        const payload = {
          avatars: [...parsedPrevAvatars, upcomingAvatarId],
        };
        try {
          const res = await axios.put(
            `/avatar-interactions/${interactionId}`,
            payload
          );
          navigate("/migoto-cms/dashboard");
        } catch (error) {
          console.error(`Error updating ${key}:`, error);
        }
      }
    }
  };

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

            {(localStorage.getItem("flow") != "UserManagement flow")&& 
            // localStorage.getItem("flow") != "UserManagement & addUser flow") && (
              (<button
                onClick={() => {
                  localStorage.setItem("TLData",JSON.stringify(TimeLineRoute["/migoto-cms/createUser/assignCourse/:id/createCourse"]));
                  localStorage.setItem("flow", "Create User and Course flow"),
                    localStorage.setItem(
                      "currentPathLocation",
                      "Create Course"
                    ),
                    navigate("createCourse"),
                    UpdateTimeline(0, {
                      status: "success",
                      description: `User Created `
                    },setSelectedData);
                    UpdateTimeline(1, {
                      status: "warning",
                      description: `In Progress`
                    },setSelectedData);
  
                }}
              >
                Create Course
                <CreateCourseIcon />
              </button>
            )}
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
              handleCancel()
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
            }}
          >
            Next {">"}
          </button>
        )}
        {currentPage == "Select Mode" && (
          <button
            className={styles.nextBtn}
            onClick={() => {
              flow == "Create Avatar flow"
                ? assignAvatarToCourse()
                : assignCourse()}}
          >
            Assign Course
          </button>
        )}
      </div>
    </div>
  );
}

export default ListofItems;
