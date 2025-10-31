import React, { useEffect, useState } from "react";
import styles from "../CourseManagement/CourseManagement.module.css";
import CourseCard from "../../Components/CourseComponent/CourseCard";
import axios from "../../service";
import { useLOIData } from "../../store";
import { Button } from "antd";
import { useNavigate } from "react-router-dom";
import CreateCourse from "../Course/CreateCourse";
import SearchIcon from "../../Icons/SearchIcon";
import { clearScenarioData, setSessionStorage } from "../../sessionHelper";

function CoursePage() {
  const [data, setData] = useState();
  const [datas, setDatas] = useState();
  let navigate = useNavigate();
  let [currentPage, setCurrentPage] = useState("showCourse");
  const { selectedData, setSelectedData } = useLOIData();
  const [size, setSize] = useState("default");
  const [search, setSearch] = useState("");
    
  const fetchListOfCourse = () => {
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
  }
  
  const handleNextPage = () => {
    if (currentPage == "showCourse" && selectedData["showCourse"]) {
      setSessionStorage("showCourse",selectedData["showCourse"])
      navigate("showModule")
      setCurrentPage("showModule");
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
    }
  }

  useEffect(()=>{
    localStorage.setItem("flow","CourseManagement flow")
    let path = window.location.pathname;
    if(path == "/migoto-cms/courseManagement"){
      setCurrentPage("showCourse");
    }
  },[window.location.pathname])

  return (
    <>
      <div className={styles.outerDetailHeader} >
        {currentPage == "showCourse" && (
          <div className={styles.OutterBox}>
            <div className={styles.headerCourse}>
                <div className={styles.headerColCourse}>
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
              {datas?.length>0 && <Button className={styles.primaryBtn}type="primary"
                onClick={() => {
                  handleNextPage()
                }}>{"Next >"}</Button>}
            </div>
          </div>
        )}
        {/* ----------------------Edit section ----------------------------- */}
        {currentPage == "editCourse" && <CreateCourse setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>}
      </div>
    </>
  );
}

export default CoursePage;