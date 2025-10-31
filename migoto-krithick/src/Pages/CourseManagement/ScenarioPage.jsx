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

function ScenarioPage() {
  const [data, setData] = useState();
  const [datas, setDatas] = useState();
  const [courseDetail, setCourseDetail] = useState();
  let navigate = useNavigate();
  let [currentPage, setCurrentPage] = useState("showScenario");
  let [page, setPage] = useState("");
  const { selectedData, setSelectedData } = useLOIData();
  const [size, setSize] = useState("default");
  const [search, setSearch] = useState("");
    
  const fetchListOfCourse = () => {
    let module_id = selectedData["showModule"] ? selectedData["showModule"] : getSessionStorage("showModule")
  
    Promise.all([
      axios.get(`/modules/${module_id}/scenarios`),
      axios.get(`/modules/${module_id}`),
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
  
  const handleNextPage = () => {
    if(selectedData["showScenario"]){
      let path = window.location.pathname.replace("showScenario","showAvatarInteraction")
      navigate(path)
      setCurrentPage("showAvatarInteraction");
      setSessionStorage("showScenario",selectedData["showScenario"]);
    }
  };

  const handlePrevious = () => {
    if (currentPage == "showScenario") {
      setSelectedData("showModule", null);
      setCurrentPage("showModule");
      const cleanedPath = window.location.pathname?.replace("/showScenario", "/showModule");
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
    if (path.endsWith("showScenario")) {
      setCurrentPage("showScenario");
    }
  },[window.location.pathname])



  return (
    <>
      <div className={styles.outerDetailHeader} >
        {currentPage == "showScenario" && (
          <div className={styles.outerDetail}>
            <div className={styles.outerDetailHead} >
              <SmallBackIcon
                onClick={() => {
                  handlePrevious();
                }}
              />
              <p>{suitableName[currentPage]?.detailHeader} Details</p>
            </div>
            <hr />
            <DetailCard courseDetail={courseDetail} currentPage={currentPage} setCurrentPage={(item)=>{setCurrentPage(item)}} setPage={(item)=>{setPage(item)}}/>
          </div>
        )}
        {currentPage == "showScenario" && (
          <div className={styles.OutterBox}>
            <div className={styles.header}>
                <div className={styles.headerCol}>
                  <p style={{ width: "150px" }}>{suitableName[currentPage].header}</p>
                  <div style={{display:"flex",alignItems:"center",gap:"4%"}}>
                    <div className={styles.searchBar}><input type="text" placeholder={`Search ${suitableName[currentPage].current}`} onChange={(e) => { setSearch(e.target.value) }} />
                      <SearchIcon className={styles.searchIconSvg} />
                    </div>
                    <Button type="primary"shape="round"size={size}className={styles.CreteBtn}
                      onClick={() => {localStorage.setItem("flow","CourseManagement flow"),navigate(suitableName[currentPage].onClick),clearScenarioData(),setSelectedData("avatarSelection",null),setSelectedData("ListofAvatars",null)}}>
                      {suitableName[currentPage].create}
                    </Button>
                  </div>
                </div>
            </div>
            <div className={styles.list}>
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
            </div>
            <div className={styles.footer}>
              <Button className={styles.cancelBtn}
                onClick={() => {
                  handlePrevious()
                }}>{"< Back"}</Button>
              <Button className={styles.primaryBtn}type="primary"
                onClick={() => {
                  handleNextPage()
                }}>{"Next >"}</Button>
            </div>
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

export default ScenarioPage;
