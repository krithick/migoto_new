import React, { useState } from "react";
import styles from "../ModesComponent/Modes.module.css";
import { CaretRightOutlined } from "@ant-design/icons";
import { Collapse, Radio, theme } from "antd";
import AvatarCard from "./AvatarCard";
import AvatarVoice from "../Card/AvatarVoice";
import { useModeData } from "../../store";

function AvatarInteraction({selected, modeData}) {
  const {isOpen,setIsOpen} = useModeData()  
  const [alreadyPlaying, setAlreadyPlaying] = useState(null);
  const [currentPlaying, setCurrentPlaying] = useState(null);

  const { token } = theme.useToken();
  const panelStyle = {
    marginBottom: 20,
    background: token.colorFillAlter,
    borderRadius: token.borderRadiusLG,
    border: "none",          
  };
  

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
          {modeData?.avatars.map((item, index) => (
            <AvatarCard key={index} data={item} currentPage="Avatars Assigned" />
          ))}
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
          {modeData?.languages.map((item, index) => (
            <AvatarCard key={index} data={item} currentPage="Languages Assigned" />
          ))}
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
          {modeData?.bot_voices.map((item, index) => (
            <AvatarVoice key={index} data={item} currentPage="Bot Voices Assigned"
            alreadyPlaying={alreadyPlaying}
            setAlreadyPlaying={setAlreadyPlaying}
            currentPlaying={currentPlaying}
            setCurrentPlaying={setCurrentPlaying}
/>
          ))}
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
          {modeData?.environments.map((item, index) => (
            <AvatarCard key={index} data={item} currentPage="Environments Assigned" />
          ))}
        </div>
        </>
      ),
      style: panelStyle,
    },
  ];

  return (
    <>
      <div className={styles.panelHeader}>
        <input
          type="checkbox"
          name="avatar"
          id="avatar"
          checked={isOpen[selected]?.enable ?? false}
          onChange={(e)=>{setIsOpen(selected,e.target.checked)}}
        />
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
        <div
          className={!isOpen[selected]?.enable ? styles.overlay : styles.overlayNone}
        ></div>
      </div>
    </>
  );
}

export default AvatarInteraction;