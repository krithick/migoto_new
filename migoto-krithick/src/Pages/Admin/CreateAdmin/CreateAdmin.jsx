import { useState } from 'react'
import styles from './CreateAdmin.module.css'
import ManualIcon from '../../../Icons/ManualIcon'
import BulkIcon from '../../../Icons/BulkIcon'
import BulkAdmin from './Upload/BulkAdmin'
import ManualAdmin from './Upload/ManualAdmin'

export default function CreateAdmin() {
  const [file, setFile] = useState("Manual Upload")

  return (
    <>
    <div className={styles.actionBox}>
      <div className={styles.actionBoxHeader}>
        <div className={`${styles.uploadBox} ${file == "Manual Upload" && styles.uploadBoxActive}`} onClick={()=>setFile("Manual Upload")}>
          <ManualIcon props="#0085DB" className={`${file == "Manual Upload" && styles.uploadManualIconActive}`}/>
          <p>Manual Upload</p>
        </div>
        <div className={`${styles.uploadBox} ${file == "Bulk Upload" && styles.uploadBoxActive}`} onClick={()=>{setFile("Bulk Upload")
        }}>
          <BulkIcon className={`${file == "Bulk Upload" && styles.uploadBulkIconActive}`}/>
          <p>Bulk Upload</p>
        </div>
      </div>
      <div className={styles.actionBoxBody}>
        {file == "Bulk Upload" ? <BulkAdmin /> : <ManualAdmin />}
      </div>
    </div>
    </>
  )
}