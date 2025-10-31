import React, { useEffect, useState } from "react";
import "./Timeline.css";
import { Timeline } from "antd";
import useGlobalStore from "../../useGlobalStore";
import { TimeLineRoute } from "../../RouteHelper/TimeLineRoute";
import { useLOIData } from "../../store";

function TimeLine() {

    const [timelineData, setTimelineData] = useState();
  const { selectedData, setSelectedData } = useLOIData();


    const renderMainTimeline = (items) =>
      items?.map((item) => ({
        dot: (
          <div className={`dottedCircle ${item.status}`}>
            <span>{item.number}</span>
          </div>
        ),
        color: item.status === "error" ? "red" : item.status === "gray" ? "gray" : undefined,
        children: (
          <>
            <span className={`timelineHeading ${item.status}`}>{item?.heading}</span>
            {item?.children ? (
              <div className="childTimeline">
                <Timeline
                  items={item?.children?.map((child, index) => ({
                    dot: <div className={`childDottedCircle ${child.status}`} />,
                    children: (
                      <span className={`timelineChildHeading ${child.status}`}>
                        {child.heading}
                      </span>
                    ),
                  }))}
                />
              </div>
            ) : (
              <div className="timelineDetails">
                <span className="title">{item?.title}</span>
                <p>{item?.description}</p>
              </div>
            )}
          </>
        ),
    }));

useEffect(() => {
}, [timelineData]);

useEffect(() => {
    const raw = localStorage.getItem("TLData");
    if (raw) {
      try {
        setTimelineData(JSON.parse(raw));
      } catch (e) {
        console.error("Invalid JSON in localStorage:", e);
      }
    }
  }, [selectedData["TLRenderer"]]);
  



  return (
    <>
      <div className="timelineContainer">
      <span className="title">Progress</span>
        {timelineData&&<Timeline className="timeline" items={renderMainTimeline(timelineData)} />}
    </div>
    </>
  );
}

export default TimeLine;
