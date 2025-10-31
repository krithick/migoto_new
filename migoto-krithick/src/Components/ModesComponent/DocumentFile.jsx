import React, { useState } from 'react'
import styles from '../ModesComponent/Modes.module.css'
import Card from '../Card/Card';
import { useModeData } from '../../store';

function DocumentFile({selected,data}) {
    let [activateMode, setActivateMode] = useState(true);
    const {isOpen,setIsOpen} = useModeData()  

  return (
    <>
      <div className={styles.panelHeader}>
        <input type="checkbox" name="avatar" id="avatar" checked={isOpen[selected]?.enable ?? false} onChange={(e)=>{setIsOpen(selected,e.target.checked),setActivateMode(e.target.checked)}} />
        <label htmlFor="avatar">Document & PDF</label>
      </div>
      <p className={styles.descrip}>
      Document provides a structured, self-paced learning experience through detailed written materials, helping you dive deep into concepts.      </p>

      <div className={styles.accordationContainer1}>
        {data?.map((item,index)=>{
            return(
            <Card data={item} index={index} currentPage={"DocumentFile"}/>
            )
        })}
        <div className={(!activateMode)?styles.overlay:styles.overlayNone}></div>
      </div>
    </>
  )
}

export default DocumentFile