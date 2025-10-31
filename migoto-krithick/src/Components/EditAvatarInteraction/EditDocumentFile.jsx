import React, { useState } from 'react'
import styles from '../ModesComponent/Modes.module.css'
import Card from '../Card/Card';
import { Button } from 'antd';
import axios from '../../service.js'
import { useLOIData, usePreviewStore, useUserPopupStore } from '../../store';
import { getSessionStorage } from '../../sessionHelper.js';

function EditDocumentFile({data}) {
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
      setSelectedData("checkAI",res.data)
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
        axios.get("/documents/")
        .then((res)=>{
            let modify = new Promise((resolve)=>{
              setIsPreview({ enable: true, msg: {overallData:res.data,prevData:data}, value: navigateTo, resolve });
            })
            modify.then((result)=>{
              if(result){
                handleUpdateAPI("assigned_documents",result)
              }
            })
        }).catch((err)=>{console.log(err);
        })
  }

  return (
    <>
    <div className={styles.panelHeader}>
      <div>
        <div className={styles.panelHeader}>
        <label htmlFor="avatar">Document & PDF</label>
      </div>
      <p className={styles.descrip}>
      Document provides a structured, self-paced learning experience through detailed written materials, helping you dive deep into concepts.      </p>
      </div>
      <div><Button onClick={()=>{handlePopUp("docsSelection")}} className={styles.addDel} type='primary'>Update Documents</Button></div>
    </div>

      <div className={styles.accordationContainer1}>
        {data?.map((item,index)=>{
            return(
            <Card data={item} index={index} currentPage={"DocumentFile"}/>
            )
        })}
      </div>
    </>
  )
}

export default EditDocumentFile