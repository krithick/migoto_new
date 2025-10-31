import React from "react";
import { VictoryPie } from "victory";
import styles from "./ProgressCard.module.css";

const ProgressCard = ({ percentage, value, color,title }) => {
  return (
    <div className={styles.card}>
      <div className={styles.chartWrapper}>
        <VictoryPie
          data={[
            { x: 1, y: percentage },
            { x: 2, y: 100 - percentage },
          ]}
          width={80}
          height={80}
          radius={23}
          innerRadius={28}
          // cornerRadius={5}
          padAngle={0}
          colorScale={[color, "#9FA8C7"]}
          style={{
            data: { stroke: "none" },
            labels: { display: "none" },
          }}
        />
        <div className={styles.centerText}>{percentage}%</div>
      </div>

      <div className={styles.info}>
        <div className={styles.label}>{title}</div>
        <div className={styles.count}>{value}</div>
      </div>
      {/* <a href="#" className={styles.link}>
        View Detail <span>→</span>
      </a> */}
    </div>
  );
};

export default ProgressCard;
