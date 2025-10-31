import React, { useEffect, useRef, useState } from "react";
import styles from "../Card/VoiceCard.module.css";
import { WaveformContianer, Wave, PlayButton } from "../Card/voiceStyle.jsx";
import WaveSurfer from "wavesurfer.js";
import PlayIcon from "../../Icons/PlayIcon.jsx";
import PauseIcon from "../../Icons/PauseIcon.jsx";
import { useLOIData } from "../../store.js";
import TickIcon from "../../Icons/TickIcon.jsx";
import PlusIcon from "../../Icons/PlusIcon.jsx";

function VoiceSelectionCard({ data, alreadyPlaying, setAlreadyPlaying, currentPlaying, setCurrentPlaying,setSelectedId, selectedId }) {
  const [playing, setPlaying] = useState(false);
  const waveformRef = useRef(null);
  const wavesurferRef = useRef(null);
  const {selectedData, setSelectedData} = useLOIData();

   
  useEffect(() => {
    const track = document.querySelector("#track-" + data.id);

    wavesurferRef.current = WaveSurfer.create({
      barWidth: 1,
      barRadius: 1,
      barGap: 5,
      barHeight: 0.5,
      cursorWidth: 1,
      container: waveformRef.current,
      backend: "WebAudio",
      height: 50,
      progressColor: "#66ff33",
      responsive: true,
      waveColor: "#000000",
      cursorColor: "transparent",
      url: data.voice_url,
    });

    wavesurferRef.current.load(track);

    // Add finish event to reset playing state
    wavesurferRef.current.on("finish", () => {
      setPlaying(false);
      if (alreadyPlaying === data.voice_url) {
        setAlreadyPlaying(null);
        setCurrentPlaying(null);
      }
    });

    return () => {
      wavesurferRef.current.destroy();
    };
  }, []);

  // Effect to handle external play/pause controls
  useEffect(() => {
    // If another audio started playing, pause this one
    if (alreadyPlaying && alreadyPlaying !== data.voice_url && playing) {
      wavesurferRef.current.pause();
      setPlaying(false);
    }
  }, [alreadyPlaying]);

  const handlePlay = (e) => {
    e.stopPropagation();

    // Get current audio source
    const currentSrc = data.voice_url;

    if (playing) {
      // If this audio is already playing, pause it
      wavesurferRef.current.pause();
      setPlaying(false);
      setAlreadyPlaying(null);
      setCurrentPlaying(null);
    } else {
      // If another audio is playing, this will trigger the useEffect to pause it
      setAlreadyPlaying(currentSrc);
      setCurrentPlaying(currentSrc);
      setPlaying(true);
      wavesurferRef.current.play();
    }
  };


  return (
    <div className={styles.voiceCardContainer2} onClick={()=>{setSelectedId(data.id)}}>
      <div className={styles.voiceCard}>
        <WaveformContianer>
          {playing ?<PauseIcon onClick={handlePlay} />:<PlayIcon onClick={handlePlay} />}
          <Wave ref={waveformRef} />
          <audio id={`track-${data.id}`} src={data.voice_url} />
        </WaveformContianer>
      </div>
      <div className={styles.voiceDescription}>
        <div>{data.gender} - {data.language_code} ({data.name})</div>
        <div>
        <div className={`${
                        selectedId?.includes(data.id)
                          ? styles.activeCard
                          : styles.selectedIndicator
                      }`}>
        {selectedId?.includes(data.id) ? (
                <TickIcon />
              ) : (
                <PlusIcon />
              )}
            </div>
        </div>
      </div>
    </div>
  );
}

export default VoiceSelectionCard;

