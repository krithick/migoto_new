// useVoiceChat.js
import { useState, useRef, useEffect } from "react";
import RecordRTC from "recordrtc";
import axios from "axios";
import { Baseurl } from "../route";

const useVoiceChat = ({
  language,
  voice,
  sessionID,
  setSessionID,
  avatar,
  mode,
  toast,
  navigate,
}) => {
  const [recording, setRecording] = useState(false);
  const [mic, setMic] = useState(true);
  const [finishButton, setFinishButton] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [audioReload, setAudioReload] = useState(false);
  const [pageReload, setPageReload] = useState(false);
  const [startAverageDurationTime, setStartAverageDurationTime] =
    useState(null);
  const [intervals, setIntervals] = useState([]);

  const recorderRef = useRef(null);
  const audioRef = useRef(new Audio());

  const getFormattedTime = () => {
    const now = new Date();
    return now.toTimeString().split(" ")[0];
  };

  const startRecording = async () => {
    try {
      if (finishButton) {
        toast.error("Your conversation has ended.");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recorderRef.current = new RecordRTC(stream, {
        type: "audio",
        mimeType: "audio/wav",
        recorderType: RecordRTC.StereoAudioRecorder,
        desiredSampRate: 16000,
      });

      recorderRef.current.startRecording();
      setRecording(true);

      if (conversationHistory.length === 0) {
        setStartAverageDurationTime(new Date().toISOString().substr(11, 8));
      }
    } catch (error) {
      console.error("Error accessing microphone", error);
      toast.error("Microphone not available...");
    }
  };

  const stopRecording = () => {
    recorderRef.current.stopRecording(() => {
      const blob = recorderRef.current.getBlob();
      postToSTT(blob);
    });
    setRecording(false);
    setMic(true);
  };

  const postToSTT = async (audioBlob) => {
    const formData = new FormData();
    formData.append("file", audioBlob, "audio.wav");
    formData.append("language", language?.title.toLowerCase());

    try {
      const response = await fetch(`${Baseurl}stt`, {
        method: "POST",
        body: formData,
      });

      const data = await response.text();
      const result = JSON.parse(data);

      if (result?.text) {
        handleUserMessage(result.text);
      } else {
        toast.error("Couldn't hear you. Please try again!");
        setMic(false);
      }
    } catch (err) {
      console.error("Error posting to STT:", err);
    }
  };

  const handleUserMessage = (message) => {
    setConversationHistory((prev) => [...prev, { role: "user", message }]);
    postToChat(message);

    if (conversationHistory.length >= 1) {
      const start = new Date(`1970-01-01T${startAverageDurationTime}Z`);
      const end = new Date(`1970-01-01T${getFormattedTime()}Z`);
      const interval = (end - start) / 1000;
      setIntervals((prev) => [...prev, interval]);
    }
  };

  const postToChat = async (message) => {
    const formData = new FormData();

    if (!sessionID) {
      const scenarioName =
        language?.title.toLowerCase() === "english"
          ? mode?.scenario
          : `${mode?.scenario}_hindi`;

      formData.append("scenario_name", scenarioName);
      formData.append("message", message);
      formData.append("name", avatar?.name);
    } else {
      formData.append("session_id", sessionID);
      formData.append("message", message);
      formData.append("name", avatar?.title);
    }

    try {
      const res = await axios.post(
        `${Baseurl}chat`,
        formData
      );
      setSessionID(res.data.session_id);

      const eventSource = new EventSource(
        `${Baseurl}chat/stream?session_id=${res.data.session_id}&name=${avatar?.title}`
      );

      let bot;

      eventSource.onmessage = (event) => {
        bot = JSON.parse(event.data);
      };

      eventSource.onerror = () => {
        handleBotResponse(bot);
        eventSource.close();
      };

      setPageReload((prev) => !prev);
    } catch (err) {
      console.error("Chat API error:", err);
    }
  };

  const handleBotResponse = async (bot) => {
    if (!bot) return;

    if (bot?.correct && mode?.name === "Training Mode") {
      await speakText(bot);
    } else {
      setConversationHistory((prev) => [
        ...prev,
        {
          role: "bot",
          message: bot?.correct_answer || bot?.response,
          correct: bot?.correct,
        },
      ]);
    }

    if (bot?.complete) {
      setFinishButton(true);
    }

    setMic(!bot?.complete);
  };

  const speakText = async (bot) => {
    const ssml = `
      <speak version='1.0' xml:lang='en-IN'>
        <voice xml:lang='en-US' xml:gender='Male' name='${voice?.voice}'>
          ${bot?.response}
        </voice>
      </speak>
    `;

    try {
      const response = await axios.post(
       
         
          responseType: "arraybuffer",
        }
      );

      const audioBlob = new Blob([response.data], { type: "audio/wav" });
      const audioURL = URL.createObjectURL(audioBlob);
      audioRef.current.src = audioURL;

      audioRef.current.play();
      setAudioReload(true);

      audioRef.current.onended = () => {
        setAudioReload(false);
        handleBotResponse(bot);
      };
    } catch (err) {
      console.error("TTS Error:", err);
    }
  };

  useEffect(() => {
    const handlePopState = () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        console.log("Audio stopped on popstate.");
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  return {
    startRecording,
    stopRecording,
    recording,
    setRecording,
    mic,
    conversationHistory,
    audioReload,
    pageReload,
  };
};

export default useVoiceChat;
