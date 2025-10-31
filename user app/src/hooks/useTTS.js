import { useRef, useState } from "react";
import instance from "../service";

const useTTS = (voice, audioReload, setMic, setAudioReload, onFinish) => {
  const audioRef = useRef(new Audio());
  // const [audioReload, setAudioReload] = useState(false);

  const speak = async (audio, correct, complete) => {
    console.log("TCL: speak -> audio", audio)
    setMic(true);
    try {
      if (!audio || typeof audio !== 'string') {
        throw new Error('Invalid audio data');
      }

      const base64ToBlob = (base64) => {
        const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: "audio/wav" });
      };

      const audioBlob = base64ToBlob(audio);
      const audioUrl = URL.createObjectURL(audioBlob);

      audioRef.current.src = audioUrl;
      audioRef.current.play();

      audioRef.current.onplay = () => setAudioReload(true);
      audioRef.current.onended = () => {
        setMic(false);
        setAudioReload(false);
        onFinish({ correct, complete });
        audioRef.current = new Audio();
      };
    } catch (err) {
      console.error("TTS error:", err);
      setMic(false);
      setAudioReload(false);
      onFinish({ correct, complete });
    }
  };

  const SkipTTS = () => {
    if (audioRef.current && audioReload) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = new Audio();
      setMic(false);
      setAudioReload(false);
    }
  };

  return { speak, audioRef, SkipTTS };
};

export default useTTS;
