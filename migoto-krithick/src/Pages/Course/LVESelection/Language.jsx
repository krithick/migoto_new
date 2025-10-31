import React, { useEffect, useState } from 'react'
import styles from '../LVESelection/LVESelection.module.css'
import LVECard from './LVECard'

function Language({selected,data}) {

  return (
    <>
      <div className={styles.boxer}>
        {data.map((item,index)=>{
            return(
                <LVECard data={item} index={index} currentPage={"Language"}/>
            )
        })}
      </div>
    </>
  )
}

export default Language