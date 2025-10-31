import React, { useEffect, useState } from "react";
import styles from "../CourseManagement/CourseManagement.module.css";
import CourseCard from "../../Components/CourseComponent/CourseCard";
import axios from "../../service";
import { useLOIData } from "../../store";
import { Button } from "antd";
import { useNavigate } from "react-router-dom";
import CreateCourse from "../Course/CreateCourse";
import CreateModule from "../Course/CreateModule";
import { div } from "three/tsl";
import SmallBackIcon from "../../Icons/smallBackIcon";
import SearchIcon from "../../Icons/SearchIcon";
import ShowAvatarInteraction from "./AvatarInteraction/ShowAvatarInteraction";
import EditScenario from "./EditScenario/EditScenario";
import DetailCard from "./DetailCard";
import { clearScenarioData, clearSessionStorage, getSessionStorage, setSessionStorage } from "../../sessionHelper";

function CourseManagement() {
  const [data, setData] = useState();
  const [datas, setDatas] = useState();
  const [avatarInteractionData, setAvatarInteractionData] = useState();
  const [courseDetail, setCourseDetail] = useState();
  let navigate = useNavigate();
  let [currentPage, setCurrentPage] = useState(window.location.pathname == "/migoto-cms/courseManagement" && "showCourse");
  let [page, setPage] = useState("");
  const { selectedData, setSelectedData } = useLOIData();
  const [size, setSize] = useState("default");
  const [search, setSearch] = useState("");
  const [isDataLoaded, setIsDataLoaded] = useState(false);
    
  const fetchListOfCourse = () => {
  let course_id = selectedData["showCourse"] ? selectedData["showCourse"] : getSessionStorage("showCourse")
  let module_id = selectedData["showModule"] ? selectedData["showModule"] : getSessionStorage("showModule")
  let scenario_id = selectedData["showScenario"] ? selectedData["showScenario"] : getSessionStorage("showScenario")
  
  if (currentPage == "showCourse") {
    axios
      .get("/courses/assignable")
      .then((res) => {
        setData(res.data);
        setDatas(res.data);
        setSearch("")
      })
      .catch((err) => {
        console.log("err: ", err);
        setData([]);
        setDatas([]);
        setSearch("")
      });
  }
  if (currentPage == "showModule") {
    Promise.all([
      axios.get(`/courses/${course_id}/modules`),
      axios.get(`/courses/${course_id}`),
    ])
      .then(([res, courseRes]) => {
        setData(res.data);
        setDatas(res.data);
        setCourseDetail(courseRes.data);
        setSearch("")
      })
      .catch((err) => {
        console.log("err: ", err);
        setData([]);
        setDatas([]);
        setCourseDetail([]);
        setSearch("")
      });
  }
  if (currentPage == "showScenario") {
    Promise.all([
      axios.get(`/modules/${module_id}/scenarios`),
      axios.get(`/modules/${module_id}`),
    ])
      .then(([res, courseRes]) => {
        setData(res.data);
        setDatas(res.data);
        setCourseDetail(courseRes.data);
        setSearch("")
        setIsDataLoaded(false)
        setAvatarInteractionData([])
      })
      .catch((err) => {
        console.log("err: ", err);
        setData([]);
        setDatas([]);
        setCourseDetail([]);
        setSearch("")
      });
  }
  if (currentPage == "showAvatarInteraction") {
    let ids = {}
    Promise.all([
      axios.get(`/scenarios/${scenario_id}`),
      axios.get(`scenarios/${scenario_id}/editing-interface`)
    ])
      .then(([res,editRes]) => {
        setCourseDetail(res?.data)
        setAvatarInteractionData(res?.data)
        setSessionStorage("template_id",res?.data?.template_id)
        setSelectedData("templateData",res?.data)
        ids = {
          "AssessModeAvatarInteractionId":res?.data?.assess_mode?.avatar_interaction,
          "LearnModeAvatarInteractionId":res?.data?.learn_mode?.avatar_interaction,
          "TryModeAvatarInteractionId":res?.data?.try_mode?.avatar_interaction
        }
        setSessionStorage("AssessModeAvatarInteractionId",res?.data?.assess_mode?.avatar_interaction)
        setSessionStorage("LearnModeAvatarInteractionId",res?.data?.learn_mode?.avatar_interaction)
        setSessionStorage("TryModeAvatarInteractionId",res?.data?.try_mode?.avatar_interaction)
        setSelectedData("EditingScenarioData",editRes?.data)
        setSelectedData("EditResponse",editRes?.data?.template_data)
        getAvatarsId(ids)
      })
      .catch((err) => {
        console.log("err: ", err);
        setAvatarInteractionData([])
      });
  }

  const getAvatarsId = async (ids) => {
    const idList = [
      { key: "LearnModeAvatarInteractionId", setKey: "LearnModeAvatar" },
      { key: "TryModeAvatarInteractionId", setKey: "TryModeAvatar" },
      { key: "AssessModeAvatarInteractionId", setKey: "AssessModeAvatar" },
    ];

    const promises = idList.map((element) => {
      return axios
        .get(`/avatar-interactions/${ids[element.key]}`)
        .then((res) => {
          setSelectedData(element.setKey, res.data?.avatars);
          setSessionStorage(element.setKey, res.data?.avatars);
        })
        .catch((err) => {
          console.log(err);
          setError(err); // Set error state if any API call fails
        });
    });

    try {
      await Promise.all(promises);
      setIsDataLoaded(true); // Set the state to indicate data is loaded
    } catch (err) {
      console.error("Error fetching avatars:", err);
    }
  };      

}
  
  const handleNextPage = () => {
    if (currentPage == "showCourse" && selectedData["showCourse"]) {
      setSessionStorage("showCourse",selectedData["showCourse"])
      navigate("showModule")
      setCurrentPage("showModule");
    } else if (currentPage == "showModule" && selectedData["showModule"]) {
      let path = window.location.pathname.replace("showModule","showScenario")
      navigate(path)
      setCurrentPage("showScenario");
      setSessionStorage("showModule",selectedData["showModule"]);
    } else if(currentPage == "showScenario" && selectedData["showScenario"]){
      let path = window.location.pathname.replace("showScenario","showAvatarInteraction")
      navigate(path)
      setCurrentPage("showAvatarInteraction");
      setSessionStorage("showScenario",selectedData["showScenario"]);
    }
  };

  const handlePrevious = () => {
    if (currentPage == "showModule") {
      setSelectedData("showCourse", null);
      setCurrentPage("showCourse");
      clearSessionStorage("showCourse")
      const cleanedPath = path?.replace("/showModule", "");
      navigate(cleanedPath);
    } else if (currentPage == "showScenario") {
      setSelectedData("showModule", null);
      setCurrentPage("showModule");
      clearSessionStorage("showModule")
      const cleanedPath = path?.replace("/showScenario", "/showModule");
      navigate(cleanedPath);
    } else if (currentPage == "showAvatarInteraction") {
      setSelectedData("showScenario", null);
      setCurrentPage("showScenario");
      clearSessionStorage("showScenario")
      const cleanedPath = path?.replace("/showAvatarInteraction", "/showScenario");
      navigate(cleanedPath);
    }
  };

  useEffect(()=>{
    if(search!=""){
      setDatas(datas.filter((item) => item?.title?.toLowerCase()?.includes(search?.toLowerCase()))) 
    }else{
      setDatas(data)
    }
  },[search])

  useEffect(() => {
    setData([])
    fetchListOfCourse();
  }, [currentPage,selectedData["checkAI"]]);

  let suitableName = {
    showCourse:{
      current:"Course",
      create: "Create Course",
      header: "List of Courses",
      detailHeader:"",
      edit:"editCourse",
      onClick:"createCourse",
    },
    showModule:{
      current:"Module",
      create: "Create Module",
      header: "List of Modules",
      detailHeader:"Course ",
      edit:"editCourse",
      onClick:"createModule"
    },
    showScenario:{
      current:"Scenario",
      create: "Create Scenario",
      header: "List of Scenarios",
      detailHeader: "Module ",
      edit:"editModule",
      onClick:"createScenario"
    },
    showAvatarInteraction:{
      current:"AvatarInteraction",
      create: "Create Scenario",
      header: "Avatar Interaction",
      detailHeader: "Scenario ",
      edit:"editScenario",
      flow: "CourseManagement & editScenario flow"
    }
  }

  useEffect(()=>{
    localStorage.setItem("flow","CourseManagement flow")
    let path = window.location.pathname;
    if(path == "/migoto-cms/courseManagement"){
      setCurrentPage("showCourse");
    } else if (path.endsWith("showModule")) {
      setCurrentPage("showModule");
    } else if (path.endsWith("showScenario")) {
      setCurrentPage("showScenario");
    } else if (path.endsWith("showAvatarInteraction")) {
      setCurrentPage("showAvatarInteraction");
    }

  },[window.location.pathname])



  return (
    <>
      <div className={styles.outerDetailHeader} >
        {(currentPage == "showModule" || currentPage == "showScenario" || currentPage == "showAvatarInteraction") && (
          <div className={styles.outerDetail}>
            <div className={styles.outerDetailHead} >
            {currentPage != "showCourse" && (
                <SmallBackIcon
                  onClick={() => {
                    handlePrevious();
                  }}
                />
              )}
            {<p>{suitableName[currentPage]?.detailHeader} Details</p>}
            </div>
            <hr />
            <DetailCard courseDetail={courseDetail} currentPage={currentPage} setCurrentPage={(item)=>{setCurrentPage(item)}} setPage={(item)=>{setPage(item)}}/>
          </div>
        )}
        {(currentPage == "showCourse" ||
          currentPage == "showModule" ||
          currentPage == "showScenario"||
          currentPage == "showAvatarInteraction") && (
          <div className={styles.OutterBox}>
            <div className={styles.header}>
                <div className={styles.headerCol}>
                  <p style={{ width: "150px" }}>{suitableName[currentPage].header}</p>
                  <div style={{display:"flex",alignItems:"center",gap:"4%"}}>
                  {currentPage != "showAvatarInteraction"&&
                    <div className={styles.searchBar}><input type="text" placeholder={`Search ${suitableName[currentPage].current}`} onChange={(e) => { setSearch(e.target.value) }} />
                      <SearchIcon className={styles.searchIconSvg} />
                    </div>}
                  {currentPage != "showAvatarInteraction"&&
                    <Button type="primary"shape="round"size={size}className={styles.CreteBtn}
                      onClick={() => {localStorage.setItem("flow","CourseManagement flow"),currentPage != "showCourse",navigate(suitableName[currentPage].onClick),clearScenarioData(),setSelectedData("avatarSelection",null),setSelectedData("ListofAvatars",null)}}>
                      {suitableName[currentPage].create}
                    </Button>}
                  </div>
                </div>
            </div>
            {/* -----------------Course Module Scenario Card ----------------------------- */}
            {currentPage!="showAvatarInteraction"&&<div className={styles.list}>
              <div className={styles.listCard}>
                {datas?.map((item, index) => {
                  return (
                    <CourseCard
                      data={item}
                      key={index}
                      currentPage={currentPage}
                    />
                  );
                })}
              </div>
            </div>}
            {(currentPage=="showAvatarInteraction" && avatarInteractionData && isDataLoaded) && <ShowAvatarInteraction activeMode={avatarInteractionData} setCurrentPage={()=>{setCurrentPage("editScenario")}} setPage={()=>{setPage("personaPopUp")}}/>}
              {<div className={styles.footer}>
                {(currentPage!="showCourse")&&<Button className={styles.cancelBtn}
                  onClick={() => {
                    handlePrevious()
                  }}>{"< Back"}</Button>}
                {(currentPage!="showAvatarInteraction") &&<Button className={styles.primaryBtn}type="primary"
                  onClick={() => {
                    handleNextPage()
                  }}>{"Next >"}</Button>}
              </div>}
            
            </div>
        )}
        {/* ----------------------Edit section ----------------------------- */}
        {
          <>
            {currentPage == "editCourse" && <CreateCourse setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}} courseDetail={courseDetail}/>}
            {currentPage == "editModule" && <CreateModule setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}} courseDetail={courseDetail}/>}
            {currentPage == "editScenario" && <EditScenario setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}} courseDetail={courseDetail} page={page}/>}
          </>
        }
      </div>
    </>
  );
}

export default CourseManagement;
