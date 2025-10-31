import React, { useState } from 'react'
import styles from '../ModesComponent/Modes.module.css'
import Card from '../Card/Card';
import { Button } from 'antd';
import axios from '../../service.js'
import { useLOIData, usePreviewStore, useUserPopupStore } from '../../store';
import { getSessionStorage } from '../../sessionHelper.js';

function EditVideoFile({selected,data}) {
    
  const {isPreview, setIsPreview} = usePreviewStore();
  const { selectedData, setSelectedData } = useLOIData();
  const { message, setMessage } = useUserPopupStore();

  const handleUpdateAPI = (loc,payload) => {
    // axios
    // .put(`/avatar-interactions/${selectedData["modifyAvaInterId"]}`, {[loc]:payload})
    let whichMode = getSessionStorage("modifyAvaInterIn")

    axios
    .put(`/avatar-interactions/${getSessionStorage(whichMode)}`, {[loc]:payload})
    .then((res) => {
      setSelectedData("checkAI", Date.now())
    })
    .catch((err) => {
      setMessage({
        enable: true,
        msg: "Something went wrong",
        state: false,
      });
});
  }

  const handlePopUp = (navigateTo) => {
        axios.get("/videos/")
        .then((res)=>{
            let modify = new Promise((resolve)=>{
              setIsPreview({ enable: true, msg: {overallData:res.data,prevData:data}, value: navigateTo, resolve });
            })
            modify.then((result)=>{
              if(result){
                handleUpdateAPI("assigned_videos",result)
              }
            })
        }).catch((err)=>{console.log(err);
        })
  }

  return (
    <>
    <div className={styles.panelHeader}>
      <div>
      <div >
        <label htmlFor="avatar">Video File</label>
      </div>
      <p className={styles.descrip}>
      Video Mode allows you to learn at your own pace through rich, visual content, offering a focused and engaging experience to absorb new skills and knowledge effectively.      </p>

      </div>
      <div><Button onClick={()=>{handlePopUp("videosSelection")}}  className={styles.addDel} type='primary'>Update Videos</Button></div>

    </div>

      <div className={styles.accordationContainer1}>
      {data?.map((item,index)=>{
            return(
                <Card data={item} index={index} currentPage={"Learn Mode video"}/>
            )
        })}


      </div>
    </>
  )
}

export default EditVideoFile