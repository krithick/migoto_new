import React, { useEffect, useState } from "react";
import styles from "../ModesComponent/Modes.module.css";
import { CaretRightOutlined } from "@ant-design/icons";
import { Collapse, Radio, theme } from "antd";
import Card from "../Card/Card.jsx";
import AvatarCard from "../ModesComponent/AvatarCard.jsx";
import VoiceCard from "../Card/VoiceCard";
import AvatarVoice from "../Card/AvatarVoice";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../store.js";
import axios from '../../service.js';
import { getSessionStorage, setSessionStorage } from "../../sessionHelper.js";

function EditAvatarInteraction({selected, modeData, setCurrentPage,setPage}) {
  const { message, setMessage } = useUserPopupStore();
  const { token } = theme.useToken();
  const panelStyle = {
    marginBottom: 20,
    background: token.colorFillAlter,
    borderRadius: token.borderRadiusLG,
    border: "none",
  };
  const {isPreview, setIsPreview} = usePreviewStore();
  const [alreadyPlaying, setAlreadyPlaying] = useState(null);
  const [currentPlaying, setCurrentPlaying] = useState(null);
  const { selectedData, setSelectedData } = useLOIData();
  let userEmpId = JSON.parse(localStorage.getItem("user"))?.id;
  const [value, setValue] = useState();

  const handleUpdateAPI = (loc,payload) => {
    let whichMode = getSessionStorage("modifyAvaInterIn")

    axios
    .put(`/avatar-interactions/${getSessionStorage(whichMode)}`, {[loc]:payload})
    .then((res) => {
      setSelectedData("checkAI", Date.now())
      setValue(payload)
    })
    .catch((err) => {
      setMessage({
        enable: true,
        msg: "Something went wrong",
        state: false,
      });
    });
  }

  useEffect(()=>{
    setValue(modeData?.layout)
  },[modeData])


  const handlePopUp = (navigateTo,value) => {
    if(navigateTo=="layout"){
            let modify = new Promise((resolve)=>{
              setIsPreview({
                enable: true,
                msg: `Are you sure you want to change the layout to- ${value} ?`,
                value: "ok/cancel",
                resolve,
              });
            })
            modify.then((result)=>{
              if(result){
                handleUpdateAPI("layout",value)
              }
            })
    }if(navigateTo=="avatarSelection"){
        axios.get("/avatars/?skip=0&limit=1000")
        .then((res)=>{
            let modify = new Promise((resolve)=>{
              setIsPreview({ enable: true, msg: {overallData:res.data,prevData:modeData.avatars}, value: navigateTo, resolve });
            })
            modify.then((result)=>{
              if(result){
                handleUpdateAPI("avatars",result)
              }
            })
        }).catch((err)=>{console.log(err);
        })
    }else if(navigateTo=="languageSelection"){
        axios.get("/languages/")
        .then((res)=>{
          let modify = new Promise((resolve)=>{
            setIsPreview({ enable: true, msg: {overallData:res.data,prevData:modeData.languages}, value: navigateTo, resolve });
          })
          modify.then((result)=>{
            if(result){
              handleUpdateAPI("languages",result)
            }
          })
        }).catch((err)=>{console.log(err);
        })
    }else if(navigateTo=="environmentSelection"){
        axios.get("/environments/")
        .then((res)=>{
          let modify = new Promise((resolve)=>{
            setIsPreview({ enable: true, msg: {overallData:res.data,prevData:modeData.environments}, value: navigateTo, resolve });
          })
          modify.then((result)=>{
            if(result){
              handleUpdateAPI("environments",result)
            }
          })
        }).catch((err)=>{console.log(err);
        })
    }else if(navigateTo=="voiceSelection"){
        axios.get("/bot-voices/")
        .then((res)=>{
          let modify = new Promise((resolve)=>{
            setIsPreview({ enable: true, msg: {overallData:res.data,prevData:modeData.bot_voices}, value: navigateTo, resolve });
          })
          modify.then((result)=>{
            if(result){
              handleUpdateAPI("bot_voices",result)
            }
          })
        }).catch((err)=>{console.log(err);
        })
    }
  }
  
  const getItems = (panelStyle) => [
    {
      key: "1",
      label: <span className={styles.panelLabel}>List Of Avatars Assigned</span>,
      children: (
        <>
        <div className={styles.cardTitle}>
            <p>List Of Avatars Assigned</p>
          </div>
          <div className={styles.ListBox}>
          {modeData?.avatars?.map((item, index) => (
            <AvatarCard key={index} data={item} currentPage="Avatars Assigned" />
          ))}
          </div>
          <div className={styles.footer}>
            {userEmpId==modeData?.created_by && <button className={styles.addDel} 
            // onClick={()=>{handlePopUp("avatarSelection")}}
            onClick={()=>{localStorage.setItem("flow","CourseManagement & editScenario flow"),setCurrentPage(),setPage(),setSessionStorage("AvatarAssignedTo","single")}}
            > Create Avatar</button>}
          </div>
        </>
      ),
      style: panelStyle,
    },
    {
      key: "2",
      label: <span className={styles.panelLabel}>List Of Language Assigned</span>,
      children: (
        <>
        <div className={styles.cardTitle}>
            <p>List Of Languages Assigned</p>
          </div>
          <div className={styles.ListBox}>
          {modeData?.languages?.map((item, index) => (
            <AvatarCard key={index} data={item} currentPage="Languages Assigned" />
          ))}
        </div>
        <div className={styles.footer}>
            {userEmpId==modeData?.created_by && <button className={styles.addDel} onClick={()=>{handlePopUp("languageSelection")}}> Add / Remove Languages</button>}
          </div>

        </>
      ),
      style: panelStyle,
    },
    {
      key: "3",
      label: <span className={styles.panelLabel}>List Of Bot Voices Assigned</span>,
      children: (
        <>
        <div className={styles.cardTitle}>
            <p>List Of Bot Voices Assigned</p>
          </div>
          <div className={styles.ListBox}>
          {modeData?.bot_voices?.map((item, index) => (
            <AvatarVoice key={index} data={item} currentPage="Bot Voices Assigned"
            alreadyPlaying={alreadyPlaying}
            setAlreadyPlaying={setAlreadyPlaying}
            currentPlaying={currentPlaying}
            setCurrentPlaying={setCurrentPlaying}/>
          ))}
          </div>
          <div className={styles.footer}>
            {userEmpId==modeData?.created_by && <button className={styles.addDel} onClick={()=>{handlePopUp("voiceSelection")}}> Add / Remove Bot Voices</button>}
          </div>

        </>
      ),
      style: panelStyle,
    },
    {
      key: "4",
      label: <span className={styles.panelLabel}>List Of Environments Assigned</span>,
      children: (
        <>
        <div className={styles.cardTitle}>
            <p>List Of Avatars Assigned</p>
          </div>
          <div className={styles.ListBox}>
          {modeData?.environments?.map((item, index) => (
            <AvatarCard key={index} data={item} currentPage="Environments Assigned" />
          ))}
        </div>
        <div className={styles.footer}>
            {userEmpId==modeData?.created_by && <button className={styles.addDel} onClick={()=>{handlePopUp("environmentSelection")}}> Add / Remove Environments</button>}
          </div>
        </>
      ),
      style: panelStyle,
    },
        {
          key: "5",
          label: <span className={styles.panelLabel}>List Of Layouts Assigned</span>,
          children: (
            <>
            <div className={styles.cardTitle}>
                <p>List Of Layouts Assigned</p>
              </div>
              <div className={styles.ListBox}>
              <div className={styles.leftSection}>
                      <Radio.Group
                        className={styles.radioGroup}
                        onChange={(e) => {handlePopUp("layout",e.target.value)}}
                        value={value}
                      >
                        <Radio className={styles.radioBtn} value={1}>
                          Layout 01
                        </Radio>
                        <Radio className={styles.radioBtn} value={2}>
                          Layout 02
                        </Radio>
                        <Radio className={styles.radioBtn} value={3}>
                          Layout 03
                        </Radio>
                      </Radio.Group>
                    </div>
                    <div className={styles.rightSection}>
                      {value==1&&<img src={"https://meta.novactech.in:6445/uploads/image/20250918094920_7e5fe4f2.png"} alt={`Layout ${value}`} />}
                      {value==2&&<img src={"https://meta.novactech.in:6445/uploads/image/20250918094825_f8189d49.png"} alt={`Layout ${value}`} />}
                      {value==3&&<img src={"https://meta.novactech.in:6445/uploads/image/20250918094700_0489f1a1.png"} alt={`Layout ${value}`} />}
                    </div>
            </div>
            </>
          ),
          style: panelStyle,
        },
    
  ];

  return (
    <>
      <div className={styles.panelHeader}>
        <label htmlFor="avatar">Avatar Interaction</label>
      </div>
      <p className={styles.descrip}>
        Avatar Interaction Mode offers an engaging, conversational learning
        experience where you interact with virtual mentors or guides, making it
        easier to understand.
      </p>
      <div className={styles.accordationContainer}>
        <Collapse
          bordered={false}
        //   defaultActiveKey={[""]}
          expandIcon={({ isActive }) => (
            <CaretRightOutlined rotate={isActive ? 90 : 0} />
          )}
          style={{ background: token.colorBgContainer }}
          items={getItems(panelStyle)}
        />
      </div>
    </>
  );
}

export default EditAvatarInteraction;