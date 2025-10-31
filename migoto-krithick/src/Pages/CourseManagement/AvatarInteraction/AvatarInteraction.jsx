import React, { useEffect, useState } from "react";
import styles from "../CourseManagement.module.css";
import axios from "../../../service";
import { useLOIData } from "../../../store";
import { Button } from "antd";
import { useNavigate } from "react-router-dom";
import SmallBackIcon from "../../../Icons/smallBackIcon";
import ShowAvatarInteraction from "./ShowAvatarInteraction";
import EditScenario from "../EditScenario/EditScenario";
import DetailCard from "../DetailCard";
import { clearSessionStorage, getSessionStorage, setSessionStorage } from "../../../sessionHelper";

function AvatarInteraction() {
  const [avatarInteractionData, setAvatarInteractionData] = useState();
  const [courseDetail, setCourseDetail] = useState();
  let navigate = useNavigate();
  let [currentPage, setCurrentPage] = useState("showAvatarInteraction");
  let [page, setPage] = useState("");
  const { selectedData, setSelectedData } = useLOIData();
  const [isDataLoaded, setIsDataLoaded] = useState(false);
    
  const fetchAvatarInteractionData = () => {
    let scenario_id = selectedData["showScenario"] ? selectedData["showScenario"] : getSessionStorage("showScenario")
    let ids = {}
    
    Promise.all([
      axios.get(`/scenarios/${scenario_id}`),
      axios.get(`scenarios/${scenario_id}/editing-interface`)
    ])
      .then(([res,editRes]) => {
        setCourseDetail(res?.data)
        setAvatarInteractionData(res?.data)
        setSessionStorage("template_id",res?.data?.template_id)
        setSelectedData("templateData",res?.data)
        ids = {
          "AssessModeAvatarInteractionId":res?.data?.assess_mode?.avatar_interaction,
          "LearnModeAvatarInteractionId":res?.data?.learn_mode?.avatar_interaction,
          "TryModeAvatarInteractionId":res?.data?.try_mode?.avatar_interaction
        }
        setSessionStorage("AssessModeAvatarInteractionId",res?.data?.assess_mode?.avatar_interaction)
        setSessionStorage("LearnModeAvatarInteractionId",res?.data?.learn_mode?.avatar_interaction)
        setSessionStorage("TryModeAvatarInteractionId",res?.data?.try_mode?.avatar_interaction)
        setSelectedData("EditingScenarioData",editRes?.data)
        setSelectedData("EditResponse",editRes?.data?.template_data)
        getAvatarsId(ids)
      })
      .catch((err) => {
        console.log("err: ", err);
        setAvatarInteractionData([])
      });
  }

  const getAvatarsId = async (ids) => {
    const idList = [
      { key: "LearnModeAvatarInteractionId", setKey: "LearnModeAvatar" },
      { key: "TryModeAvatarInteractionId", setKey: "TryModeAvatar" },
      { key: "AssessModeAvatarInteractionId", setKey: "AssessModeAvatar" },
    ];

    const promises = idList.map((element) => {
      return axios
        .get(`/avatar-interactions/${ids[element.key]}`)
        .then((res) => {
          setSelectedData(element.setKey, res.data?.avatars);
          setSessionStorage(element.setKey, res.data?.avatars);
        })
        .catch((err) => {
          console.log(err);
        });
    });

    try {
      await Promise.all(promises);
      setIsDataLoaded(true);
    } catch (err) {
      console.error("Error fetching avatars:", err);
    }
  };

  const handlePrevious = () => {
    setSelectedData("showScenario", null);
    const cleanedPath = window.location.pathname?.replace("/showAvatarInteraction", "/showScenario");
    navigate(cleanedPath);
  };

  useEffect(() => {
    fetchAvatarInteractionData();
  }, [currentPage,selectedData["checkAI"]]);

  let suitableName = {
    showAvatarInteraction:{
      current:"AvatarInteraction",
      create: "Create Scenario",
      header: "Avatar Interaction",
      detailHeader: "Scenario ",
      edit:"editScenario",
      flow: "CourseManagement & editScenario flow"
    }
  }

  useEffect(()=>{
    localStorage.setItem("flow","CourseManagement flow")
    let path = window.location.pathname;
    if (path.endsWith("showAvatarInteraction")) {
      setCurrentPage("showAvatarInteraction");
    }
  },[window.location.pathname])

  return (
    <>
      <div className={styles.outerDetailHeader} >
        {currentPage == "showAvatarInteraction" && (
          <div className={styles.outerDetail}>
            <div className={styles.outerDetailHead} >
              <SmallBackIcon
                onClick={() => {
                  handlePrevious();
                }}
              />
              <p>{suitableName[currentPage]?.detailHeader} Details</p>
            </div>
            <hr />
            <DetailCard courseDetail={courseDetail} currentPage={currentPage} setCurrentPage={(item)=>{setCurrentPage(item)}} setPage={(item)=>{setPage(item)}}/>
          </div>
        )}
        {currentPage == "showAvatarInteraction" && (
          <div className={styles.OutterBox}>
            <div className={styles.header}>
                <div className={styles.headerCol}>
                  <p style={{ width: "150px" }}>{suitableName[currentPage].header}</p>
                </div>
            </div>
            {(avatarInteractionData && isDataLoaded) && <ShowAvatarInteraction activeMode={avatarInteractionData} setCurrentPage={()=>{setCurrentPage("editScenario")}} setPage={()=>{setPage("personaPopUp")}}/>}
            <div className={styles.footer}>
              <Button className={styles.cancelBtn}
                onClick={() => {
                  handlePrevious()
                }}>{"< Back"}</Button>
            </div>
          </div>
        )}
        {/* ----------------------Edit section ----------------------------- */}
        {currentPage == "editScenario" && <EditScenario setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{}} courseDetail={courseDetail} page={page}/>}
      </div>
    </>
  );
}

export default AvatarInteraction;