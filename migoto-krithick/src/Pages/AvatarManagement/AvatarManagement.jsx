import React, { useEffect, useState } from "react";
import styles from "../CourseManagement/CourseManagement.module.css";
import CourseCard from "../../Components/CourseComponent/CourseCard";
import axios from '../../service'
import { useLOIData } from "../../store";
function AvatarManagement() {
  const [data, setData] = useState();
  let [currentPage, setCurrentPage] = useState("showAvatar");
  const { selectedData, setSelectedData } = useLOIData();

const getAvatarInteractions = () => {
    axios
      .get("/avatars/?skip=0&limit=1000")
      .then((res) => {
        setData(res.data)
      })
      .catch((err) => {
        console.log("err: ", err);
      });

  };

//   const handleNextPage = () => {
//         if(currentPage=="showCourse" && selectedData[currentPage]){
//             setCurrentPage("showModule");
//         }else if(currentPage=="showModule" && selectedData[currentPage]){
//             setCurrentPage("showScenario");
//         }
//   }
//   const handlePrevious = () => {
//             setSelectedData("showModule",null)
//             setSelectedData("showScenario",null)
//             setSelectedData("showCourse",null)
//             setCurrentPage("showCourse");
//   }

//   useEffect(()=>{
//     handleNextPage();
//   },[selectedData])

  useEffect(() => {
    getAvatarInteractions();
  },[]);

  return (
    <>
      <div className={styles.OutterBox}>
        <div className={styles.list}>
            <div className={styles.listCard}>
          {data?.map((item, index) => {
            return <CourseCard data={item} key={index} currentPage={currentPage} />;
          })}
          </div>
        </div>
        <div className={styles.BtnGroup}>
          {/* {currentPage!="showCourse"&&<button onClick={()=>{handlePrevious()}}>{"<"}Back</button>} */}
          {/* {currentPage!="showScenario"&&<button className={styles.nextBtn} onClick={()=>{handleNextPage()}}>Next {">"}</button>} */}
        </div>
      </div>
    </>
  );
}

export default AvatarManagement;
