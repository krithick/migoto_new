import React, { useEffect, useState, useRef, Suspense } from "react";
import IconSelection from "../AvatarCreation/AvatarCoustomization/IconSelection";
import styles from "../AvatarViewer/AvatarViewer.module.css";
import { Canvas } from "@react-three/fiber";
import Character from "../AvatarCreation/AvatarCoustomization/Character";
import { Html, Loader, OrbitControls } from "@react-three/drei";
import CameraController from "../AvatarCreation/AvatarCoustomization/CameraController";
import { Button } from "antd";
import VoiceSelectionCard from "../../Components/AssignALVEPopup/VoiceSelectionCard";
import VoiceList from "./VoiceList";
import LightHelper from "./AvatarComponent/LightHelper";
import ModelLoader from "./AvatarComponent/ModelLoader";
import axios from "../../service.js";
import { getSessionStorage } from "../../sessionHelper.js";
function AvatarViewer({ backFunction }) {
  const [data, setData] = useState([]);
  const [glb, setGlb] = useState([]);
  const [name, setName] = useState();
  const [gender, setGender] = useState();
  const [animation, setAnimation] = useState();
  const [speak, setSpeak] = useState();
  const [audioReload, setAudioReload] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const audioRef = useRef(new Audio());

  useEffect(() => {
    axios.get(`/avatars/${getSessionStorage("AvatarPreview")}`)
    .then((res) => {
      setGlb(res.data.glb);
      setData(res.data.selected);
      setName(res.data.name)
      setGender(res.data.gender)
      setAnimation(res.data.animation)
    });
  }, []);

  const handleTTS = async () => {
    if(speak && name && !isPlaying && !isLoading){
        setIsLoading(true);
        setIsPlaying(true);
        
        let text = `Hi there! i am ${name} , How can i help you?`
        const formData = new FormData();
        formData.append("message", text);
        formData.append("voice_id", speak);
        try {
          const response = await axios.post("/speech/tts", formData,{
              headers: {
                  "Content-Type": "multipart/form-data",
                  Authorization: localStorage.getItem("migoto-cms-token"),
                },          
              responseType: "arraybuffer"});
    
          // Clean up previous audio URL
          if (audioRef.current.src) {
            URL.revokeObjectURL(audioRef.current.src);
          }
    
          const audioBlob = new Blob([response.data], { type: "audio/wav" });
          const audioUrl = URL.createObjectURL(audioBlob);
    
          // Create new audio element to avoid range request issues
          audioRef.current = new Audio();
          audioRef.current.src = audioUrl;
          audioRef.current.preload = "auto";
          
          audioRef.current.oncanplaythrough = () => {
            audioRef.current.play().catch(err => console.error("Play error:", err));
          };
    
          audioRef.current.onplay = () => setAudioReload(true);
          audioRef.current.onended = () => {
            URL.revokeObjectURL(audioUrl);
            setAudioReload(false);
            setIsPlaying(false);
            setIsLoading(false);
          };
        } catch (err) {
          console.error("TTS error:", err);
          setIsPlaying(false);
          setIsLoading(false);
        }
    }
  };

  useEffect(()=>{
    if(modelLoaded && speak && name){
      handleTTS();
    }
  },[modelLoaded, speak, name])

  // Remove the second useEffect to prevent duplicate calls


  return (
    <>
      <div className={styles.modelContainer}>
        <VoiceList setSpeak={(item)=>setSpeak(item)} isDisabled={isPlaying} gender={gender} />
            
        <div className={styles.sceneContainer}>
          <Canvas
            //   gl={{ preserveDrawingBuffer: true, logarithmicDepthBuffer: true }}
            camera={{ position: [0, 0, 1], fov: 45 }}
            shadows
          >

            <LightHelper />
            {/* <OrbitControls enablePan={true} makeDefault /> */}
            <Suspense fallback={
                <Html>
                <Loader />
                </Html>
            }/>
                <ModelLoader glb={glb} data={data} onLoad={() => setModelLoaded(true)} animation={animation} isPlaying={isPlaying} audioRef={audioRef}/>
          </Canvas>
        </div>
      </div>
      <div className={styles.footer}>
        <div className={styles.container}>
          <Button
            type="primary"
            onClick={() => {
                backFunction();
            }}
          >
            Skip
          </Button>
        </div>
      </div>
    </>
  );
}

export default AvatarViewer;
