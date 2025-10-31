import React, { useState } from "react";
import styles from "../AssignCourse/AssignBulkCourse.module.css";
import CourseList from "../../Components/AssignBulkCourseComp/CourseList";
import ModuleList from "../../Components/AssignBulkCourseComp/ModuleList";
import LoiHeader from "../../Components/AssignBulkCourseComp/LoiHeader";

function AssignBulkCourse() {
  let [datas, setDatas] = useState([]);
  let [data, setData] = useState([]);
  let [activeCourse, setActiveCourse] = useState("all");
  let [filterData, setFilterData] = useState("");
  const [selectedCourse, setSelectedCourse] = useState([])

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <LoiHeader
          filterData={filterData}
          datas={datas}
          setData={setData}
          setDatas={setDatas}
          activeCourse={activeCourse}
          setActiveCourse={setActiveCourse}
        />
      </div>
      <div className={styles.body}>
        <div className={`${styles.courseListBox} ${selectedCourse.length > 0 ? styles.small : ''}`}>
          <CourseList 
            data={data} 
            setDatas={setDatas}
            setData={setData}
            selectedCourse={selectedCourse}
            setSelectedCourse={setSelectedCourse}
          />
        </div>
        <div className={`${styles.moduleListBox} ${selectedCourse.length > 0 ? styles.open : ''}`}>
          <ModuleList 
            selectedCourse={selectedCourse}
            />
        </div>
      </div>
    </div>
  );
}

export default AssignBulkCourse;
