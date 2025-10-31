import React, { useEffect, useRef, useState } from "react";
import styles from "../CourseProgress/CourseProgress.module.css";
import EditIcon from "../../../Icons/EditIcon";
import BackIcon from "../../../Icons/BackIcon";
import CompletedCoursesIcon from "../../../Icons/CompletedCoursesIcon";
import AssignedCourseIcon from "../../../Icons/AssignedCourseIcon";
import PendingCoursesIcon from "../../../Icons/PendingCoursesIcon";
import Card from "../../../Components/Card/Card";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import axios from "../.././../service";
import UserDetailSideBar from "../../../Components/UserDetailBox/UserDetailSideBar";


export default function CourseProgress({val,Swap}) {
  let [currentPage, setCurrentPage] = useState("assignedCourse");
  let navigate = useNavigate()
  let [viewAll, setViewAll] = useState(false);
  let [page, setPage] = useState("Course Progress");
  const { id } = useParams();
  const [data, setData] = useState();
  const fetchCourses = async () => {
    try {
      // const userList = await axios.get(`/auth/users/${id}/courses`);
      const userList = await axios.get(`/course-assignments/user/${id}/courses`);
      setData(userList.data);
    } catch (e) {
      console.log("Unable to fetch users", e);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const newdata = [
  ];

  function handleClick(page) {
    setPage(page);
    if (page == "Course Progress") {
      setViewAll(false);
    } else {
      setViewAll(true);
    }
  }

  return (
    <>
      <div className={styles.tab}>
        <UserDetailSideBar val={val} Swap={()=>Swap()} />

        <div className={styles.mainBox}>
          <div className={styles.mainHeader}>
            <div className={styles.HeaderBoxy}>
              {page !== "Course Progress" ? (
                <BackIcon onClick={() => handleClick("Course Progress")} />
              ) : (
                <></>
              )}
              <p>{page}</p>
            </div>

            {page === "Course Progress" ? (
              <div className={styles.assignBtn} onClick={() => {
                navigate(`assignCourse/${id}`);
              }}>Assign Course</div>
            ) : (
              <></>
            )}
          </div>

          <div className={styles.mainSection}>
            {!viewAll && (
              <>
                <div className={styles.sectionContent1}>
                  {/* 1 */}
                  <div className={styles.content1Sub}>
                    <div className={styles.subIcon}>
                      <AssignedCourseIcon />
                    </div>
                    <div className={styles.subValueBox}>
                      <div className={styles.subValueTitle}>
                        Assigned Courses
                      </div>
                      <div className={styles.subValueNumber}>{data?.length}</div>
                    </div>
                  </div>
                  {/* 2 */}
                  <div className={styles.content1Sub}>
                    <div className={styles.subIcon2}>
                      <CompletedCoursesIcon />
                    </div>
                    <div className={styles.subValueBox}>
                      <div className={styles.subValueTitle}>
                        Completed Courses
                      </div>
                      <div className={styles.subValueNumber2}>{data?.filter(course => course?.completed).length}
                      </div>
                    </div>
                  </div>
                  {/* 3 */}
                  <div className={styles.content1Sub3}>
                    <div className={styles.subIcon3}>
                      <PendingCoursesIcon />
                    </div>
                    <div className={styles.subValueBox}>
                      <div className={styles.subValueTitle}>
                        Pending Courses
                      </div>
                      <div className={styles.subValueNumber3}>{data?.filter(course => course?.completed=="false").length}</div>
                    </div>
                  </div>
                </div>

                <div className={styles.sectionContent2}>
                  <div className={styles.content2Header}>
                    <div>Assigned Courses</div>
                  </div>

                  <div className={styles.content2CardsBox}>
                    {data && data.map((item, index) => {
                      return (
                        <Card
                          data={item}
                          key={index}
                          currentPage={currentPage}
                        />
                      );
                    })}
                  </div>
                </div>
              </>
            )}

            {/* {viewAll && page == "In progress courses" ? (
              <>
                <div className={styles.sectionNewContent2}>
                  {newdata.map((item, index) => {
                    return (
                      <Card data={item} key={index} currentPage={currentPage} />
                    );
                  })}
                </div>
              </>
            ) : (
              <></>
            )}

            {viewAll && page == "Completed courses" ? (
              <>
                <div className={styles.sectionNewContent2}>
                  {newdata.map((item, index) => {
                    return (
                      <Card data={item} key={index} currentPage={currentPage} />
                    );
                  })}
                </div>
              </>
            ) : (
              <></>
            )} */}
          </div>
        </div>
      </div>
    </>
  );
}
