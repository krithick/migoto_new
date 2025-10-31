import React, { useEffect, useState } from "react";
import styles from "../AssignBulkCourseComp/ModuleList.module.css";
import { CaretRightOutlined } from "@ant-design/icons";
import { Collapse, Radio, theme } from "antd";
import axios from "../../service.js";

function ModuleList({ selectedCourse }) {
  let [moduleData, setModuleData] = useState([]);

  const { token } = theme.useToken();
  const panelStyle = {
    marginBottom: 20,
    background: token.colorFillAlter,
    borderRadius: token.borderRadiusLG,
    border: "none",
  };

  useEffect(() => {
    if (selectedCourse && selectedCourse.length > 0) {
      axios
        .get(`/courses/${selectedCourse[0]}/modules`)
        .then((res) => {
          setModuleData(res.data);
        })
        .catch((err) => {
          console.log("err: ", err);
        });
    }
  }, [selectedCourse]);

  const getItems = (panelStyle) =>
    moduleData?.map((item, index) => ({
      key: index,
      label: (
        <>
          <div className={styles.moduleList}>
            <div>
            <input
                  type="checkbox"
                  onChange={() => handleCheckboxChange()}
                />
            </div>
            <div className={styles.image}>
              <img src={item?.thumbnail_url} alt="" />
            </div>
            <div className={styles.text}>
              <p>Module Title</p>
              {item.title || item.name || "Module"}
            </div>
          </div>
        </>
      ),
      children: (<>
        <p>List of Scenario</p>
        <div className={styles.scenarioList}>
          {item.scenarios.map((scenario, index) => (
            <div className={styles.scenario} key={index}>
              <div className={styles.image}>
                <img src={scenario.thumbnail_url} alt="" />
              </div>
              <div className={styles.text}>
                <p>Scenario Title</p>
                {scenario.title || scenario.name || "Scenario"}
              </div>
            </div>
          ))}
        </div>
      </>),
      style: panelStyle,
    })) || [];

  return (
    <div className={styles.moduleBox}>
      <div className={styles.accordationContainer}>
        <Collapse
          bordered={false}
          //   defaultActiveKey={[""]}
          expandIcon={({ isActive }) => (
            <CaretRightOutlined rotate={isActive ? 90 : 0} />
          )}
          style={{ background: token.colorBgContainer }}
          items={getItems(panelStyle)}
        />
      </div>
    </div>
  );
}

export default ModuleList;
