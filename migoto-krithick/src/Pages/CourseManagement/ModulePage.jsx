import React, { useEffect, useState } from "react";
import styles from "../CourseManagement/CourseManagement.module.css";
import CourseCard from "../../Components/CourseComponent/CourseCard";
import axios from "../../service";
import { useLOIData } from "../../store";
import { Button } from "antd";
import { useNavigate } from "react-router-dom";
import CreateCourse from "../Course/CreateCourse";
import CreateModule from "../Course/CreateModule";
import SmallBackIcon from "../../Icons/smallBackIcon";
import SearchIcon from "../../Icons/SearchIcon";
import DetailCard from "./DetailCard";
import { clearScenarioData, clearSessionStorage, getSessionStorage, setSessionStorage } from "../../sessionHelper";

function ModulePage() {
  const [data, setData] = useState();
  const [datas, setDatas] = useState();
  const [courseDetail, setCourseDetail] = useState();
  let navigate = useNavigate();
  let [currentPage, setCurrentPage] = useState("showModule");
  console.log('currentPage: ', currentPage);
  let [page, setPage] = useState("");
  const { selectedData, setSelectedData } = useLOIData();
  const [size, setSize] = useState("default");
  const [search, setSearch] = useState("");
  const [isDataLoaded, setIsDataLoaded] = useState(false);
    
  const fetchListOfCourse = () => {
  let course_id = selectedData["showCourse"] ? selectedData["showCourse"] : getSessionStorage("showCourse")
  let module_id = selectedData["showModule"] ? selectedData["showModule"] : getSessionStorage("showModule")
  let scenario_id = selectedData["showScenario"] ? selectedData["showScenario"] : getSessionStorage("showScenario")
    
    Promise.all([
      axios.get(`/courses/${course_id}/modules`),
      axios.get(`/courses/${course_id}`),
    ])
      .then(([res, courseRes]) => {
        setData(res.data);
        setDatas(res.data);
        setCourseDetail(courseRes.data);
        setSearch("")
        setIsDataLoaded(false)
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
    if(selectedData["showModule"]){
      let path = window.location.pathname.replace("showModule","showScenario")
      navigate(path)
      setCurrentPage("showScenario");
      setSessionStorage("showModule",selectedData["showModule"]);
    }
  };

  const handlePrevious = () => {
    if (currentPage == "showModule") {
      setSelectedData("showCourse", null);
      setCurrentPage("showCourse");
      const cleanedPath = window.location.pathname?.replace("/showModule", "");
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
    }
  }

  useEffect(()=>{
    localStorage.setItem("flow","CourseManagement flow")
    let path = window.location.pathname;
    if (path.endsWith("showModule")) {
      setCurrentPage("showModule");
    }
  },[window.location.pathname])

  return (
    <>
      <div className={styles.outerDetailHeader} >
        {currentPage == "showModule" && (
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
        {currentPage == "showModule" && (
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
        {currentPage == "editCourse" && <CreateCourse currentPage={currentPage} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}} courseDetail={courseDetail}/>}
        {currentPage == "editModules" && <CreateModule setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}} courseDetail={courseDetail}/>}
      </div>
    </>
  );
}

export default ModulePage;