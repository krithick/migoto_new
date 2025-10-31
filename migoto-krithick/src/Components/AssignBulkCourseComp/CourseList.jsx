import React, { useEffect, useMemo } from "react";
import axios from "../../service.js";
import styles from "../AssignBulkCourseComp/CourseList.module.css";
function CourseList({
  data,
  setDatas,
  setData,
  setSelectedCourse,
  selectedCourse,
}) {
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

  const handleCheckboxChange = (courseId) => {
    setSelectedCourse((prev) =>
      prev.includes(courseId)
        ? prev.filter((id) => id !== courseId)
        : [...prev, courseId]
    );
  };

  return (
    <div className={styles.tableBox}>
      <table className={styles.courseTable}>
        <thead className={styles.tableHead}>
          <tr className={styles.thead}>
            <th className={styles.emptybox}> </th>
            <th className={styles.courseHeadTitle}>Course</th>
            {selectedCourse?.length==0 && <>
            <th className={styles.courseHeadDescription}>Description</th>
            <th className={styles.courseHead4}>Created At</th>
            <th className={styles.courseHead5}>Creater Role</th>
            </>}
          </tr>
        </thead>
        <tbody className={styles.courseBody}>
          {data?.map((course, index) => (
            <tr
              className={`${
                selectedCourse.includes(course.id) ? styles.selected : ""
              }`}
              key={course.id || index}
              onClick={(e) => {
                handleCheckboxChange(course.id);
              }}
            >
              <td className={styles.emptybox}>
                <input
                  type="checkbox"
                  checked={selectedCourse.includes(course.id)}
                  onClick={(e) => e.stopPropagation()} // prevent row click
                  onChange={() => handleCheckboxChange(course.id)}
                />
              </td>
              <td className={styles.courseTitle}>
                <div className={styles.image}>
                  <img src={course?.thumbnail_url} alt="" />
                </div>
                <div className={styles.text}>
                  <p>course Title</p>
                  {course.title || course.name || "Course"}
                </div>
              </td>
              {selectedCourse?.length==0 && <>
                <td title={course.description || "-"} className={styles.courseDescription}>
                  {course.description
                    ? course.description.length > 140
                      ? course.description.substring(0, 140) + "..."
                      : course.description
                    : "-"}
                </td>
                <td>
                  {course?.created_at
                    ? new Date(course.created_at).toLocaleDateString()
                    : "-"}
                </td>
                <td>{course.creater_role || "-"}</td>
              </>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default CourseList;
