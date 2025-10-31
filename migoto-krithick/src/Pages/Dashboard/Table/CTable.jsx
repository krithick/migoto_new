import React, { useState, useEffect } from "react";
import styles from "./CTable.module.css";
import axios from "../../../service"; // adjust the path if needed

function CTable() {
  const [data, setData] = useState([]);
  const [selectedData, setSelectedData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {

      try {
        const res = await axios("/dashboard/user-analysis?limit=10&offset=0");

        const transformed = res.data.map((item, idx) => ({
          id: item.id,
          userName: item.user.name,
          employeeId: item.user.employee_id,
          email: item.user.email,
          scenarioName: item.scenario_name,
          overallScore: item.overall_score,
          // status: item.user.status || "-",
        }));
        setData(transformed);
      } catch (err) {
        console.error("Failed to fetch user analysis:", err);
      }
    };

    fetchData();
  }, []);

  const handleAllSelect = (e) => {
    if (e.target.checked) {
      setSelectedData(data.map((item) => item.employeeId));
    } else {
      setSelectedData([]);
    }
  };

  const handleIndividualSelect = (item, e) => {
    if (e.target.checked) {
      setSelectedData((prev) => [...prev, item]);
    } else {
      setSelectedData((prev) => prev.filter((value) => value !== item));
    }
  };

  return (
    <div className={styles.previewContainerTable}>
      <table>
        <thead>
          <tr>
            <th>S.no</th>
            <th>User Name</th>
            {/* <th>Employee ID</th> */}
            <th>Email Address</th>
            <th>Scenario Type</th>
            <th>Overall Score</th>
            {/* <th>Status</th> */}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={item.id}>
              <td>{index + 1}</td>
              <td>{item.userName}</td>
              {/* <td>{item.employeeId}</td> */}
              <td>{item.email}</td>
              <td>{item.scenarioName}</td>
              <td>{item.overallScore}</td>
              {/* <td>{item.assigneeEmpId}</td>
              <td>{item.status}</td> */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default CTable;