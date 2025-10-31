import React from "react";

import styles from '../ThumbnailCard/ThumbnailCard.module.css'

function ThumbnailCard({title}) {

    return (
        <>
            <div className={styles.mainDiv}>
                <div className={styles.picDiv}>
                    {/* <img src="" alt="" /> */}
                </div>

                <div className={styles.infoDiv}>
                    <div>Video Title</div>
                    <div>{title}</div>
                </div>
            </div>
        </>
    )
}

export default ThumbnailCard
