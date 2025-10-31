
import React, { useState, useEffect } from "react";
import styles from '../../AvatarCreation/Voice.module.css'
import VoiceCard from "../../../Components/Card/VoiceCard"
import { useLOIData } from "../../../store";


function LVEVoice({data}) {
  let [currentPage, setCurrentPage] = useState("Voice");
  const [alreadyPlaying, setAlreadyPlaying] = useState(null);
  const [currentPlaying, setCurrentPlaying] = useState(null);
  const [voiceData, setVoiceData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  let [activeCourse, setActiveCourse] = useState("all");

  const { selectedData, setSelectedData } = useLOIData();


  const handleSelectData = () => {
    //card selection
    const currentData = selectedData[currentPage] || [];

    let updatedData;

    if (currentData?.includes(data.id)) {
      // Remove item
      updatedData = currentData.filter((id) => id !== data.id);
    } else {
      // Add item
      updatedData = [...currentData, data.id];
    }
    setSelectedData(currentPage, updatedData);
  };


  const handleChangeCourse = (creator) => {
    setActiveCourse(creator);
    if (creator === "all") {
      setFilteredData(voiceData);
    } else {
      setFilteredData(voiceData.filter((item) => item.created_by === creator));
    }
  };

  return (
    <>
      <div className={styles.voiceOutter}>
        <div className={styles.voiceBody}>
          {data.map((item, index) => (
            <VoiceCard
              data={item}
              key={index}
              currentPage={currentPage}
              alreadyPlaying={alreadyPlaying}
              setAlreadyPlaying={setAlreadyPlaying}
              currentPlaying={currentPlaying}
              setCurrentPlaying={setCurrentPlaying}
            />
          ))}
        </div>
      </div>
    </>
  );
}

export default LVEVoice;
