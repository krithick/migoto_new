import React, { useEffect, useState } from "react";
import "./Timeline.css";
import { Timeline } from "antd";
import useGlobalStore from "../../useGlobalStore";
import { useRenderStore } from "../../useGlobalStore";

function CustomTimeline() {
  const { myArray } = useGlobalStore();
  const isRender = useRenderStore((state) => state.isRender);

  const [timelineData, setTimelineData] = useState(() => {
    const savedTimeline = localStorage.getItem("timeline");
    return savedTimeline ? JSON.parse(savedTimeline) : [];
  });

  useEffect(() => {
    const savedTimeline = localStorage.getItem("timeline");
    setTimelineData(savedTimeline ? JSON.parse(savedTimeline) : []);
  }, [isRender]);

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
          <span className={`timelineHeading ${item.status}`}>{item.heading}</span>
          {item.children ? (
            <div className="childTimeline">
              <Timeline
                items={item.children.map((child, index) => ({
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

  return (
    <div className="timelineContainer">
      <span className="title">Progress</span>
      <Timeline className="timeline" items={renderMainTimeline(timelineData)} />
    </div>
  );
}

export default CustomTimeline;
