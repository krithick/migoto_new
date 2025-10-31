import React, { useState } from "react";
import styles from "../Card/Card.module.css";
import PreviewIcon from "../../Icons/PreviewIcon";
import { useLOIData } from "../../store";
import TickIcon from "../../Icons/TickIcon";
import PlusIcon from "../../Icons/PlusIcon";

function AvatarSelectionCard({ data, setSelectedId, selectedId,currentPage }) {

  return (
    <div
      className={`${styles.card1} ${selectedId?.includes(data.id) ? styles.activeCard0 : ""}`}
      onClick={() => {setSelectedId(data.id)}} >
      <div className={styles.imgContainer}>
        <img
          src={data?.thumbnail_url ? data.thumbnail_url : "/avatarImg.png"}
          alt=""
        />
        {/* image overlay content only for course,scenario,module */}
        {
          <div className={styles.details}>
            {/* <div className={styles.title}>
              <p>Character Name</p>
              <div>{data?.name}</div>
            </div> */}
            <div className={styles.status}>
              {/* <p>Age</p>
              <div>{data?.age}</div> */}
            </div>
          </div>
        }
          <div className={styles.gradient}></div>
      </div>
      {
        <div className={styles.contentContainer}>
          {currentPage=="avatarSelection"&&<div className={styles.titles}>
            <p>Name</p>
            <div>{data?.name}</div>
          </div>}
          {currentPage!="avatarSelection"&&
          <div className={styles.titles}>
            <div >Title</div>
            <div title={data?.title?.replaceAll(/[_-]/g, " ")}>{data?.title?.length > 25 ? data?.title?.slice(0, 25)?.replaceAll(/[_-]/g, " ") + "..." : data?.title?.replaceAll(/[_-]/g, " ")}</div>
              {/* <div>{data?.title?.replaceAll(/[_-]/g, " ")}</div> */}
            </div>          
          }
          <div
            className={`${
              selectedId?.includes(data.id)
                ? styles.activeCard1
                : styles.selectedIndicator
            }`}
          >
            {selectedId?.includes(data.id) ? (
              <TickIcon />
            ) : (
              <PlusIcon />
            )}
          </div>
        </div>
      }
    </div>
  );
}

export default AvatarSelectionCard;
