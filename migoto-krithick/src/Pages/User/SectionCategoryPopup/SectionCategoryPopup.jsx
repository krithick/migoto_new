import React from "react";
import styles from '../SectionCategoryPopup/SectionCategoryPopup.module.css'
import PlusIcon from "../../../Icons/PlusIcon";

function SectionCategoryPopup({ props, setCategoryStatus , setSectionStatus}) {

    function handleNewSection() {
        const form = document.querySelector(`.${styles.formTileContainer}`);
        const formTile = document.querySelector(`.${styles.formTileBox}`);

        if (form && formTile) {
            form.appendChild(formTile.cloneNode(true));
        }
    }
    function handleClose (){
        // setCategoryStatus(false)
        setSectionStatus(false)
    }


    return (
        <div className={styles.popupScreen}>
            <div className={styles.popupBox}>


                <div className={styles.headerBox}>
                    <div className={styles.title}>
                        Add Section
                    </div>
                    <div className={styles.closeBtn}
                        onClick={() => { handleClose() }}
                    >X
                    </div>
                </div>

                <div className={styles.bodyBox}>
                    {
                        props === "Add category" ? <div className={styles.titleTile}>
                            <p>Category Title</p>
                            <input type="text" placeholder="AIM" />
                        </div> : <></>
                    }

                    <div className={styles.buttonTile}>
                        <div>Add Sections</div>
                        <div className={styles.addBtn} onClick={() => { handleNewSection() }}>
                            <PlusIcon />
                            <div>Add New Section</div>
                        </div>
                    </div>

                    <div className={styles.formTileContainer}>
                        <div className={styles.formTileBox}>
                            <p>Section title</p>
                            <input type="text" placeholder="Enter section name" />
                            <p>Section Input</p>
                            <input type="text" placeholder="Enter section name" />
                        </div>

                    </div>

                    <div className={styles.bottomBtnBox}>
                        <div className={styles.cancelBtn} onClick={() => { handleClose() }}>
                            Cancel
                        </div>

                        <div className={styles.saveBtn}>
                            Save
                        </div>
                    </div>
                </div>

            </div>
        </div>
    )
}

export default SectionCategoryPopup