import React, { useEffect, useState } from "react";
import { useLOIData } from "../../store";
import styles from "../../Components/SelectedDATA/SelectedData.module.css";
import { Card } from "antd";
import Item from "antd/es/list/Item";

function SelectedData() {
  const { selectedData, setSelectedData } = useLOIData();
  const [data, setData] = useState(selectedData || {});

  useEffect(() => {
    setData(selectedData);
  }, [selectedData]);

  if (false) return null;
  return (
    <>
      <div className={styles.card}>
        <div className={styles.headies}>Stored Data</div>
        <div className={styles.bodies}>
        {Object.keys(data).map((key) => (
          <Card>
            <p>{key}: </p>
            {Array.isArray(data[key])
              ? data[key].map((val, i) => <span key={i}>{val}, </span>)
              : typeof data[key] === "object" && data[key] !== null
              ? "[object Object]"
              : data[key]}
          </Card>
        ))}
        </div>
        <div className={styles.footies}></div>
      </div>
    </>
  );
}

export default SelectedData;
