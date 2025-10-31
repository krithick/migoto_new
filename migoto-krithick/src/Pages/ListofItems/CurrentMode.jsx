import React, { useEffect, useState } from "react";
import styles from "../ListofItems/ListofMode.module.css";
import AvatarInteraction from "../../Components/ModesComponent/AvatarInteraction";
import VideoFile from "../../Components/ModesComponent/VideoFile";
import DocumentFile from "../../Components/ModesComponent/DocumentFile";
import { useModeData } from "../../store";
import axios from '../../service'

function CurrentMode({activeCourse,data}) {
  let [selected, setSelected] = useState(activeCourse.title+" avatar");
  let [activateMode, setActivateMode] = useState(false);
  const [modeData, setModeData] = useState()
  const [file, setFile] = useState();
  const [video, setVideo] = useState()
  const [pdf, setPdf] = useState()
  const {isOpen,setIsOpen} = useModeData()  

  useEffect(()=>{
    setSelected(activeCourse.title+ " avatar");
  },[activeCourse])

  const fetchVideoPdf = (path,api) => {
    
    axios
    .post(`${path}`,{'ids':api})
    .then((res) => {
      setFile(res.data)
    })
    .catch((err) => {
      console.log("err: ", err);
      setFile([])
    });
  }


  const fetchMode = (api) => {

    axios
    .get(`/avatar-interactions/${api}?expand=avatars&expand=languages&expand=bot_voices&expand=environments`)
    .then((res) => {
      setModeData(res.data)
      if(res.data.assigned_documents){
        setVideo(res.data.assigned_videos)
        setPdf(res.data.assigned_documents)
      }
    })
    .catch((err) => {
      console.log("err: ", err);
      setModeData([])
    });
  }

  useEffect(()=>{     
    if(activeCourse.title=="Learn Mode" && isOpen[activeCourse.title]?.enable){
      if(isOpen[activeCourse.title+ " avatar"]?.enable && selected=="Learn Mode avatar"){
        fetchMode(data[0]?.learn_mode?.avatar_interaction);
      }else if(isOpen[activeCourse.title+" video"]?.enable && selected=="Learn Mode video"){
        fetchVideoPdf(`/videos/bulk/`,video); 
      }else if(isOpen[activeCourse.title+" pdf"]?.enable && selected=="Learn Mode pdf"){
        fetchVideoPdf(`/documents/bulk/`,pdf);
      }
    }else if(activeCourse.title=="Try Mode" && isOpen[activeCourse.title]?.enable){
      fetchMode(data[0]?.try_mode?.avatar_interaction);
    }else if(activeCourse.title=="Assess Mode" && isOpen[activeCourse.title]?.enable){
      fetchMode(data[0]?.assess_mode?.avatar_interaction);
    }
  },[activeCourse,isOpen,selected])

  
  
  return (
    <>
      <div className={styles.loiBodyOuter}>
        <div className={styles.loiBodyHead}>
          <div>{activeCourse.title}</div>
          <p>
          {activeCourse.description}</p>
          <div>
            <input type="checkbox" name="mode" id="mode"   checked={isOpen[activeCourse.title]?.enable ?? false} onChange={(e)=>{setIsOpen(activeCourse.title,e.target.checked),setIsOpen(activeCourse.title+" avatar",e.target.checked)}}/>
            <label htmlFor="mode">{activeCourse.label}</label>
          </div>
        </div>
        <div className={styles.loiBody}>
          <div className={styles.sideBar}>
            <div
              className={`${styles.unselected} ${
                selected == `${activeCourse.title+" avatar"}` ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected(`${activeCourse.title+" avatar"}`);
              }}
            >
              Avatar Interaction
            </div>
            {activeCourse.title=="Learn Mode"&&<div
              className={`${styles.unselected} ${
                selected == `${activeCourse.title+" video"}` ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected(`${activeCourse.title+" video"}`);
                !isOpen["Learn Mode video"]&&setIsOpen("Learn Mode video",true)
              }}
            >
              Video File
            </div>}
            {activeCourse.title=="Learn Mode"&&<div
              className={`${styles.unselected} ${
                selected == `${activeCourse.title+" pdf"}` ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected(`${activeCourse.title+" pdf"}`);
                !isOpen["Learn Mode pdf"]&&setIsOpen("Learn Mode pdf",true);

              }}
            >
              Document & PDF
            </div>}
          </div>
          <div className={styles.contentPanel}>
            {selected == `${activeCourse.title+" avatar"}` && <AvatarInteraction selected={selected} modeData={modeData} />}
            {selected == `${activeCourse.title+" video"}` && <VideoFile selected={selected} data={file} />}
            {selected == `${activeCourse.title+" pdf"}` && <DocumentFile selected={selected} data={file} />}
          </div>
          <div className={!(isOpen[activeCourse.title]?.enable)?styles.overlay:styles.overlayNone}></div>
        </div>
      </div>
    </>
  );
}

export default CurrentMode;
