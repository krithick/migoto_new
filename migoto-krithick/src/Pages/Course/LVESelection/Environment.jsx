import React, { useState } from 'react'
import styles from '../LVESelection/LVESelection.module.css'
import LVECard from './LVECard'

function Environment({selected,data}) {

  return (
    <>
      <div className={styles.boxer}>
        {data.map((item,index)=>{
            return(
                <LVECard data={item} index={index} currentPage={"Environment"}/>
            )
        })}
      </div>
    </>
  )
}

export default Environment