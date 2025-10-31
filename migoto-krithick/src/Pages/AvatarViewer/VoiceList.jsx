import React, { useEffect, useState } from 'react'
import styles from '../AvatarViewer/VoiceList.module.css'
import axios from '../../service.js'
import { useLOIData } from '../../store'

function VoiceList({setSpeak, isDisabled, gender}) {
    const [voiceData, setVoiceData] = useState([]);
    const { selectedData, setSelectedData } = useLOIData();

    useEffect(()=>{
        axios
        .get(`/bot-voices/`)
        .then((res) => {
          // Filter voices by gender if gender prop is provided
          const filteredVoices = gender ? res.data.filter(voice => voice.gender == gender) : res.data;
          setVoiceData(filteredVoices);
          // Don't automatically set speak to prevent duplicate TTS calls
        })
        .catch((err) => {
          console.log("err:", err);
        });
    },[gender])

  return (
    <>
    <div className={styles.voiceContainer}>
    <div>VoiceList</div>
    <div className={`${styles.voiceList}`}>
        {voiceData.map((voice, index) => (
            <div 
                key={voice.id || index} 
                className={`${styles.voiceItem}  ${isDisabled? styles.fff:""}`} 
                onClick={()=>{!isDisabled && setSpeak(voice.voice_id)}}
            >
                <div className={styles.voiceName}>{voice.name} - {voice.gender}</div>
                <div className={styles.languageCode}>{voice.language_code}</div>
            </div>
        ))}
    </div>
    </div>
    </>
  )
}

export default VoiceList