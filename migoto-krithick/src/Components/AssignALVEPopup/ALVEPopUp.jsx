import React, { useEffect, useState } from "react";
import { usePreviewStore } from "../../store";
import SearchIcon from "../../Icons/SearchIcon";
import styles from '../AssignALVEPopup/ALVEPopUp.module.css'
import AvatarVoice from "../Card/AvatarVoice";
import VoiceSelectionCard from "../AssignALVEPopup/VoiceSelectionCard.jsx";
import AvatarCard from "../ModesComponent/AvatarCard";
import AvatarSelectionCard from "../AssignALVEPopup/AvatarSelectionCard.jsx";

function ALVEPopUp() {
  const {isPreview, setIsPreview} = usePreviewStore();
  let check = ["avatarSelection","languageSelection", "voiceSelection", "environmentSelection","docsSelection","videosSelection"]
  const [data, setData] = useState([])
  const [prevData, setPrevData] = useState([])
  let [assigned, setAssigned] = useState([])
  let [unassigned, setUnassigned] = useState([])
  let [selectedId, setSelectedId] = useState([])
  let [nav, setNav] = useState("overall")
  let [search, setSearch] = useState("")
  const [alreadyPlaying, setAlreadyPlaying] = useState(null);
  const [currentPlaying, setCurrentPlaying] = useState(null);

  useEffect(()=>{
    if(isPreview.msg?.overallData?.length>0){
        setData(isPreview.msg?.overallData)
        setPrevData(isPreview.msg?.prevData)
    }
  },[isPreview.msg])

  useEffect(() => {
    if (data && prevData) {
        const prevIds = prevData.map(obj => obj?.id);
        setSelectedId(prevIds) //for collectiong from users
        setAssigned(data.filter(item => prevIds.includes(item?.id)));
        setUnassigned(data.filter(item => !prevIds.includes(item?.id)));
      }
  }, [prevData]);
  
  const handleCancel = () => {
    if (isPreview.resolve) isPreview.resolve(false);
    setIsPreview({ enable: false, msg: "", value: isPreview.value, resolve: null });
  };

  const handleProceed = () => {
    if (isPreview.resolve) isPreview.resolve(selectedId);
    setIsPreview({ enable: false, msg: "", value: isPreview.value, resolve: null });
  };

  // const checkContent = {
  //   overall: data,
  //   assigned,
  //   unassigned
  // }[nav];

  const handleSelection = (id) => {
    setSelectedId((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const getFilteredData = () => {
    const list = {
      overall: data,
      assigned,
      unassigned,
    }[nav] || [];
  
    if (!search?.trim()) return list;
  
    return list.filter(item =>
      item?.name?.toLowerCase().includes(search.toLowerCase())
    );
  };
  
  const checkContent = getFilteredData();
  
  
  
  if (!isPreview.enable || !check.includes(isPreview.value)) return null;

  
  return (
    <div className={styles.popBg}>
      <div className={styles.popupContainer}>
        <div className={styles.header}>
          <div className={styles.searchContainer}>
            <div className={styles.iconHolder}>
              <SearchIcon />
            </div>
            <input
              onChange={(e) => {setSearch(e.target.value)}}
              type="text"
              className={styles.search}
              placeholder="Search ..."
            />
          </div>
        </div>

        <div className={styles.contentBox}>
          <div className={styles.langBoxHolder}>
            <div className={styles.LangBox}>
              <div className={styles.langHeader}>
                <p
                  onClick={() => {setNav("overall")}}
                  className={nav == "overall" ?styles.activeP:""}
                >
                  Overall
                </p>
                <p
                  onClick={() => {setNav("assigned")}}
                  className={nav == "assigned" ?styles.activeP:""}
                >
                  Assigned
                </p>
                <p
                  onClick={() => {setNav("unassigned")}}
                  className={nav == "unassigned" ?styles.activeP:"" }
                >
                  Un Assigned
                </p>
              </div>

                {/* for language and environment */}
              {(isPreview.value == "environmentSelection" || isPreview.value == "languageSelection")&&
                <div className={styles.langContainer}>
                {checkContent?.map((item, index) => (
                  <div
                    className={styles.singleLangCard}
                    key={item.id}
                    onClick={()=>{handleSelection(item?.id)}}
                  >
                    <div className={styles.imgHolder}>
                        <img src={item?.thumbnail_url} alt="" />
                    </div>
                    <input
                      type="checkbox"
                      className={styles.checkBox}
                      checked={selectedId?.includes(item?.id)}
                    />
                  </div>
                ))}
              </div>}
              {/* for voice  */}
              {isPreview.value == "voiceSelection"&&
              <div className={styles.langContainer}>
                {checkContent?.map((item, index) => (
                    <VoiceSelectionCard data={item} 
                    alreadyPlaying={alreadyPlaying}
                    setAlreadyPlaying={setAlreadyPlaying}
                    currentPlaying={currentPlaying}
                    setCurrentPlaying={setCurrentPlaying}
                    setSelectedId={(id)=>{handleSelection(id)}}
                    selectedId={selectedId}
                    />
                ))}
              </div>}
                {/* for avatar */}
              {(isPreview.value == "avatarSelection"||isPreview.value == "docsSelection"||isPreview.value == "videosSelection")&&
              <div className={styles.langContainer}>
                {checkContent?.map((item, index) => (
                    <AvatarSelectionCard data={item}
                    currentPage = {isPreview.value}
                    setSelectedId={(id)=>{handleSelection(id)}}
                    selectedId={selectedId}
                    />
                ))}
              </div>}
            </div>
          </div>

          <div className={styles.footer}>
            <div className={styles.cancelBtn} onClick={()=>{handleCancel()}}>Cancel</div>
            <div className={styles.saveBtn} onClick={()=>{handleProceed()}}>Save</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ALVEPopUp;
