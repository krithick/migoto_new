import React, { useEffect, useState } from 'react'
import styles from '../AssignBulkCourseComp/LoiHeader.module.css'
import FilterIcon from '../../Icons/FilterIcon';
import SearchIcon from '../../Icons/SearchIcon';
import CreateCourseIcon from '../../Icons/CreateCourseIcon';
import axios from '../../service'
import BackIcon from '../../Icons/BackIcon';
function LoiHeader({filterData,datas,setData, data, setDatas, activeCourse, setActiveCourse}) {
  let [currentPage, setCurrentPage] = useState("List Of Courses");

  const fetchListOfCourse = () => {
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
  };

  useEffect(() => {
    fetchListOfCourse();
  }, []);


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

  return (
    <div className={styles.loiHeader}>
    <div className={styles.loiHeaderLeft}>
      <div className={styles.loiActive}>
        <div className={styles.heading}>
            <BackIcon />
          <p>List of Courses</p>
          {/* {filterOn && (
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
          )} */}
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

  )
}

export default LoiHeader