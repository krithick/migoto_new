import React, { useEffect, useState } from "react";
import styles from "../AvatarInteraction/ShowAvatarInteraction.module.css";
import axios from "../../../service.js";
import { useLOIData, useModeData } from "../../../store";
import { Button } from "antd";
import EditAvatarInteraction from "../../../Components/EditAvatarInteraction/EditAvatarInteraction.jsx";
import EditVideoFile from "../../../Components/EditAvatarInteraction/EditVideoFile.jsx";
import EditDocumentFile from "../../../Components/EditAvatarInteraction/EditDocumentFile.jsx";
import { setSessionStorage } from "../../../sessionHelper.js";

function ShowAvatarInteraction({ activeMode , setCurrentPage,setPage}) {
  let [selected, setSelected] = useState("avatar");
  let [choose, setChoose] = useState("Learn Mode");
  let [activateMode, setActivateMode] = useState(false);
  const [modeData, setModeData] = useState([]);
  const [file, setFile] = useState();
  const [video, setVideo] = useState();
  const [pdf, setPdf] = useState();
  const { isOpen, setIsOpen } = useModeData();
  const { selectedData, setSelectedData } = useLOIData();

  const fetchVideoPdf = (path, api) => {
    axios
      .post(`${path}`, { ids: api })
      .then((res) => {
        setFile(res.data);
      })
      .catch((err) => {
        console.log("err: ", err);
        setFile([]);
      });
  };

  const fetchMode = (api,whichMode) => {
    // setSelectedData("modifyAvaInterId",api)
    setSelectedData("modifyAvaInterIn",whichMode)
    setSessionStorage("modifyAvaInterIn",whichMode)
    setModeData([])
    axios
      .get(
        `/avatar-interactions/${api}?expand=avatars&expand=languages&expand=bot_voices&expand=environments&expand=assigned_documents&expand=assigned_videos`
      )
      .then((res) => {
        setModeData(res.data);
        let avatarData = [];
        res.data.avatars.map((val, i) => {
          avatarData.push(val.id);
        });
        setSelectedData("avatarsId", avatarData)
        setVideo(res.data.assigned_videos);
        setPdf(res.data.assigned_documents);
      })
      .catch((err) => {
        console.log("err: ", err);
        setModeData([]);
      });
  };

  useEffect(() => {
    if (choose == "Learn Mode") {
      fetchMode(activeMode?.learn_mode?.avatar_interaction,"LearnModeAvatarInteractionId");
    }else if(choose == "Try Mode"){
      fetchMode(activeMode?.try_mode?.avatar_interaction,"TryModeAvatarInteractionId");
    }else if(choose == "Assess Mode"){
      fetchMode(activeMode?.assess_mode?.avatar_interaction,"AssessModeAvatarInteractionId");
    }
  }, [selected, choose, selectedData["checkAI"]]);

  return (
    <>
      <div className={styles.loiBodyOuter}>

        {/* -------Header------- */}
        {/* <div className={styles.loiBodyHead}> */}
          <div className={styles.loiHeader}>
            <div className={styles.totalBox}>
              <div
                className={`${styles.box} ${choose === "Learn Mode" ? styles.active : ""}`}
                onClick={() => {setChoose("Learn Mode"),setSelected(`${"avatar"}`)}}>Learn Mode
              </div>
              <div
                className={`${styles.box} ${choose =="Try Mode" ? styles.active : ""}`}
                onClick={() => {setChoose("Try Mode"),setSelected(`${"avatar"}`)}}>Try Mode
              </div>
              <div
                className={`${styles.box} ${choose =="Assess Mode"? styles.active : ""}`}
                onClick={() => {setChoose("Assess Mode"),setSelected(`${"avatar"}`)}}>Assess Mode  
              </div>
            </div>
            {/* <div className={styles.btnDiv}>
            <Button size="default" className={styles.editBtn}>{`Edit ${choose}`}</Button>
            </div> */}
          </div>
        {/* </div> */}
        <div className={styles.loiBody}>
          {/* -------sideBar------- */}
          <div className={styles.sideBar}>
            <div
              className={`${styles.unselected} ${
              selected == `${"avatar"}` ? styles.selected : ""}`}
              onClick={() => {setSelected(`${"avatar"}`);}}>Avatar Interaction</div>
            {choose=="Learn Mode"&&<div
              className={`${styles.unselected} ${selected == `${"video"}` ? styles.selected : ""}`}
              onClick={() => {setSelected(`${"video"}`);}}>Video File</div>}
            {choose=="Learn Mode"&&<div
              className={`${styles.unselected} ${selected == `${"pdf"}` ? styles.selected : ""}`}
              onClick={() => {setSelected(`${"pdf"}`);}}>Document & PDF</div>}
          </div>

          {/* -------content----------- */}
          <div className={styles.contentPanel}>
            {(selected == `${"avatar"}`&& modeData) && (
              <EditAvatarInteraction modeData={modeData} setCurrentPage={()=>setCurrentPage()} setPage={()=>setPage()}/>
            )}
            {selected == `${"video"}` && video && (
              <EditVideoFile data={video} />
            )}
            {selected == `${"pdf"}` && pdf && (
              <EditDocumentFile data={pdf} />
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default ShowAvatarInteraction;
