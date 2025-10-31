import { useState, useRef } from "react";
import RecordRTC from "recordrtc";
import toast from "react-hot-toast";
import instance from "../service";

const useSTT = (
  setMic,
  conversationHistory,
  startTotalDurationTime,
  setStartTotalDurationTime,
  voice,
  setRecording,
  onResult
) => {
  const [audioStream, setAudioStream] = useState(null);
  const recorderRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setAudioStream(stream);
      recorderRef.current = new RecordRTC(stream, {
        type: "audio",
        mimeType: "audio/wav",
        recorderType: RecordRTC.StereoAudioRecorder,
        desiredSampRate: 16000,
      });
      recorderRef.current.startRecording();
      setRecording(true);
      if (conversationHistory.length == 0 && startTotalDurationTime == null) {
        const start = new Date().getTime(); // Get current time in milliseconds
        setStartTotalDurationTime(start);
      }
    } catch (error) {
      toast.error("Microphone not available...");
      console.error("Error accessing mic:", error);
    }
  };

  const stopRecording = async () => {
    console.log("Start Recording");

    if (!recorderRef.current) return;
    recorderRef.current.stopRecording(async () => {
      const blob = recorderRef.current.getBlob();
      await sendToSTT(blob);
    });
    setRecording(false);
    setMic(true);
  };

  const sendToSTT = async (blob) => {
    const formData = new FormData();
    formData.append("file", blob, "audio.wav");
    formData.append("language_code", voice.language_code);

    try {
      const response = await instance.post("/speech/stt", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
        },
      });

      // if (!response.ok) throw new Error("STT API failed");
      const result = response.data.text;

      if (result) {
        onResult(result);
      } else {
        toast.error("Couldn't hear you. Please try again!");
        setMic(false);
      }
    } catch (error) {
      setMic(false);
      console.error("Error posting to STT:", error);
    }
  };

  return { startRecording, stopRecording, audioStream };
};

export default useSTT;
