import React, { useEffect, useState } from "react";
import { VictoryPie, VictoryLabel } from "victory";
// import styles from "./Chart1.module.css";
import styles from "./Chart.module.css";
import ProgressCard from "./ProgressCard/ProgressCard";
import axios from "../../../service"; // adjust path if needed

function Chart() {
  const [courseStats, setCourseStats] = useState({
    total_courses: 0,
    created_by_me: 0,
    created_by_my_company: 0, //other admin key
    created_by_superadmin: 0,
    created_by_mother_company: 0,
  });

  useEffect(() => {
    const fetchCourseStats = async () => {      
      try {
        const res = await axios.get("/dashboard/course-stats");
        setCourseStats(res.data);
      } catch (err) {
        console.error("Error fetching course stats:", err);
      }
    };

    fetchCourseStats();
  }, []);

  const data = [
    { x: 1, y: courseStats.created_by_me, color: "#DB5AEE" },
    { x: 2, y: courseStats.created_by_my_company, color: "#FFB536" }, //other admin key
    { x: 3, y: courseStats.created_by_superadmin, color: "#217EFD" },
    { x: 4, y: courseStats.created_by_mother_company, color: "#F3654A" },
  ];

  const total = courseStats.total_courses;

  return (
    <div className={styles.chartContainer}>
      <div className={styles.overallPie}>
      <svg className="pieSvg" width={"100%"} viewBox="0 0 400 400">
        <VictoryPie
          className="chart"
          standalone={false}
          innerRadius={100}
          data={data}
          colorScale={data.map((item) => item.color)}
          labels={() => null}
          padAngle={1}
        />
        <VictoryLabel
          textAnchor="middle"
          verticalAnchor="middle"
          x={200}
          y={160}
          style={{ fontSize: 18, fill: "#9FA8C7" }}
          text="Overall Courses"
        />
        <VictoryLabel
          textAnchor="middle"
          verticalAnchor="middle"
          x={200}
          y={200}
          style={{ fontSize: 40, fontWeight: "bold", fill: "#217EFD" }}
          text={total}
        />
      </svg>
    </div>
      

      <div className={styles.appContainer}>
        <ProgressCard color={data[0].color} percentage={Math.round((data[0].y / total) * 100) || 0} value={data[0].y || 0} title={"Created By Me"} />
        <ProgressCard color={data[1].color} percentage={Math.round((data[1].y / total) * 100) || 0} value={data[1].y || 0} title={"Created By other Admins "} />
        <ProgressCard color={data[2].color} percentage={Math.round((data[2].y / total) * 100) || 0} value={data[2].y || 0} title={"Created By Super Admin"} />
        <ProgressCard color={data[3].color} percentage={Math.round((data[3].y / total) * 100) || 0} value={data[3].y || 0} title={"Pre-Defined Courses"} />
      </div>
    </div>
  );
}

export default Chart;