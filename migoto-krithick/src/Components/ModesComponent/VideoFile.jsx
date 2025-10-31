import React, { useState } from 'react'
import styles from '../ModesComponent/Modes.module.css'
import { useModeData } from '../../store';
import Card from '../Card/Card';

function VideoFile({selected,data}) {
    let [activateMode, setActivateMode] = useState(true);
    const {isOpen,setIsOpen} = useModeData()  
    
  return (
    <>
      <div className={styles.panelHeader}>
        <input type="checkbox" name="avatar" id="avatar" checked={isOpen[selected]?.enable ?? false} onChange={(e)=>{setIsOpen(selected,e.target.checked),setActivateMode(e.target.checked)}}/>
        <label htmlFor="avatar">Video File</label>
      </div>
      <p className={styles.descrip}>
      Video Mode allows you to learn at your own pace through rich, visual content, offering a focused and engaging experience to absorb new skills and knowledge effectively.      </p>

      <div className={styles.accordationContainer1}>
      {data?.map((item,index)=>{
            return(
                <Card data={item} index={index} currentPage={"Learn Mode video"}/>
            )
        })}

      <div className={(!activateMode)?styles.overlay:styles.overlayNone}></div>

      </div>
    </>
  )
}

export default VideoFile