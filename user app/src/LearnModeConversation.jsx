import React, { useEffect, useRef, useState } from "react";
import HeaderMenu from "./components/HeaderMenu";
import AssignSideMenu from "./components/AssignSideMenu";
import { useNavigate } from "react-router";

import toast from "react-hot-toast";

import FinishConversationButtons from "./components/FinishConversationButtons";
import ConversationLayout1 from "./components/ConversationLayout1";
import useLLM from "./hooks/useLLM";
import useTTS from "./hooks/useTTS";
import useSTT from "./hooks/useSTT";
import instance from "./service";
import LearnModeVideo from "./components/LearnModeVideo";
import LearnModeDocument from "./components/LearnModeDocument";

const LearnModeConversation = () => {
  const [isThinking, setIsThinking] = useState(false);
  const navigate = useNavigate();
  // State variables for managing various aspects of the component
  // const [close, setClose] = useState(false);
  const [viewPage, setViewPage] = useState("conversation");
  const [language, setLanguage] = useState({
    code: "en-US",
    id: "ec489817-553a-4ef4-afb5-154f78f041b6",
    name: "English",
    thumbnail_url: "string",
  });
  const [layout, setLayout] = useState(null);
  const [recording, setRecording] = useState(false);
  const [reload, setReload] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [voice, setVoice] = useState({
    language_code: "en-US",
    name: "Andrew",
    voice_id: "en-IN-AashiNeural",
  });
  const [environment, setEnvironment] = useState(null);
  const [avatar, setAvatar] = useState(null);
  const [mode, setMode] = useState(null);
  const [pageReload, setPageReload] = useState(false);
  const [finishButton, setFinishButton] = useState(false);
  const [mic, setMic] = useState(false);
  const [audioReload, setAudioReload] = useState(false);
  const [avatarAction, setAvatarAction] = useState("Neutral");
  const [userInput, setUserInput] = useState("");
  const [sessionId, setSessionId] = useState(null);

  const avatars = {
    persona_id: [{ name: "Trainer" }],
    glb: [
      {
        file: "./Character/Da_Body_B1.glb",
        thumbnail: "string",
        name: "body",
      },
      {
        file: "./Character/Da_Pant_Pt3.glb",
        thumbnail: "string",
        name: "pant",
      },
      {
        file: "./Character/Da_Shirt_St1.glb",
        thumbnail: "string",
        name: "shirt",
      },
      {
        file: "./Character/Da_Hair_Hr1.glb",
        thumbnail: "string",
        name: "hair",
      },
    ],
    animation: "./Character/Da_Armature.glb",
  };

  const [startTotalDurationTime, setStartTotalDurationTime] = useState(null);
  const [startAverageDurationTime, setStartAverageDurationTime] =
    useState(null);
  const [intervals, setIntervals] = useState([]);

  // Fetching user-selected data from local storage on component mount
  useEffect(() => {
    if (localStorage.getItem("migoto-token") == null) {
      navigate("/login", { replace: true });
    }
    fetchAssignedLearnModeDetails();
    // if (localStorage.getItem("migoto-course")) {
    //   setCourse(JSON.parse(localStorage.getItem("migoto-course")));
    // }

    if (localStorage.getItem("migoto-mode")) {
      setMode(JSON.parse(localStorage.getItem("migoto-mode")));
    }
  }, [reload]);

  // fetch assigned avatar details
  const fetchAssignedLearnModeDetails = async () => {
    try {
      let avatarIntraction;
      if (localStorage.getItem("migoto-mode") != null) {
        avatarIntraction = JSON.parse(localStorage.getItem("migoto-mode"));
      }
      // Fetch and load token
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
      };
      instance
        .get(
          `/avatar-interactions/${avatarIntraction?.avatar_interaction}?expand=avatars&&expand=languages&&expand=voices&&expand=environments&&expand=bot_voices`,
          {
            headers,
          }
        )
        .then((response) => {
          setAvatar({ selected: response.data.avatars[0] });
          // setLanguage(response.data.languages[1]);
          // setVoice(response.data.bot_voices[0]);
          setEnvironment(response.data.environments[0]);
          setLayout(response.data.layout);
        })
        .catch((error) => {
          console.error("Error fetching learning conversation :", error);
        });
    } catch (error) {
      console.error("Error fetching learning conversation :", error);
    }
  };

  // Function to mark the previous user message as incorrect if the bot's response is incorrect
  const markPreviousUserWrongIfBotWrong = (history) => {
    const updated = [...history];

    updated.forEach((msg, idx) => {
      if (msg.role === "bot" && msg.correct === false && idx > 0) {
        if (updated[idx - 1].role === "user") {
          updated[idx - 1].correct = false;
        }
      }
    });

    return updated;
  };

  // Final conversation history after processing
  const finalConversationHistory =
    markPreviousUserWrongIfBotWrong(conversationHistory);

  // Handler for processing STT (Speech-to-Text) results
  const handleSTTResult = (text) => {
    if (text) {
      sendMessage(text);
      setMic(true);
    } else {
      toast.error("Couldn't hear you. Please try again!");
    }
  };

  // Handler for processing bot responses
  const handleBotResponse = (bot) => {
    if (bot?.emotion) setAvatarAction(bot.emotion);
    if (bot?.correct !== undefined) {
      if (bot?.correct == true) {
        setIsThinking(false); // Hide thinking when TTS starts
        speak(bot.audio, bot.correct, bot.complete);
        console.log("TCL: handleBotResponse -> bot.audio", bot)
        // speak(
        //   bot.response.replace(/[\*\#]|\[CORRECT\]/g, ""),
        //   bot.correct,
        //   bot.complete
        // );
      } else {
        setIsThinking(false); // Hide thinking
        setMic(false);
      }
    }
  };

  // Handler for speech end events
  const handleSpeechEnd = ({ complete }) => {
    if (complete) setFinishButton(true);
    setMic(false);
    setPageReload(!pageReload);
  };

  // Hook for STT API integration
  const { startRecording, stopRecording, audioStream } = useSTT(
    setMic,
    conversationHistory,
    startTotalDurationTime,
    setStartTotalDurationTime,
    voice,
    setRecording,
    handleSTTResult
  );

  // Hook for TTS (Text-to-Speech) API integration
  const { speak, audioRef, SkipTTS } = useTTS(
    voice,
    audioReload,
    setMic,
    setAudioReload,
    handleSpeechEnd
  );

  // Hook for LLM (Language Model) API integration
  const { sendMessage: llmSendMessage } = useLLM(
    setMic,
    voice,
    conversationHistory,
    startTotalDurationTime,
    setStartTotalDurationTime,
    startAverageDurationTime,
    setIntervals,
    avatar,
    mode,
    language,
    setConversationHistory,
    handleBotResponse,
    setSessionId,
    sessionId
  );

  // Wrapper to handle thinking state
  const sendMessage = (message) => {
    setIsThinking(true);
    llmSendMessage(message);
  };

  // Function to navigate to the report page
  const NavigateFunction = () => {
    navigate("/report", { replace: true });
  };

  const handlePopState = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0; // Reset to the beginning
      console.log("Audio stopped");
    }
  };

  useEffect(() => {
    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);
  return (
    <div className="absolute inset-0 backdrop-blur-[68px]">
      <div className="h-screen w-screen relative">
        <HeaderMenu
          audioRef={audioRef}
          index={"1"}
          disable={
            conversationHistory.length == 0 || finishButton ? true : false
          }
          reload={reload}
          setReload={setReload}
        />
        <div className="h-[35.5rem] xl:h-[36.5rem] 2xl:h-[54rem] w-screen flex items-center">
          <div className="h-full w-screen place-content-center px-[10rem] xl:px-[6rem] 2xl:px-[10rem] pb-[5rem]">
            <div className="h-[50px] xl:h-[40px] 2xl:h-[50px] flex items-center text-[#000000] text-[16px] xl:text-[14px] 2xl:text-[16px] font-medium">
              Assigned Courses
            </div>
            <div className="h-full w-full bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px] flex">
              <div className="h-full w-[80rem]">
                <div className="h-[5rem] xl:h-[4rem] 2xl:h-[5rem] w-full flex items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <div className="w-full h-full">
                    <div className="flex items-end text-center h-[50%]">
                      <span className="text-[16px] xl:text-[14px] 2xl:text-[16px] xl:w-[10rem] 2xl:w-[10rem] text-[#131F49]">
                        Learn Mode
                      </span>
                    </div>
                    <div className="w-full h-[50%] flex justify-center space-x-5">
                      <button
                        onClick={() => {
                          if (audioRef.current) {
                            audioRef.current.pause();
                            audioRef.current.currentTime = 0; // Reset to the beginning
                            console.log("Audio stopped");
                          }
                          setAudioReload(false);
                          setMic(false);
                          setViewPage("conversation");
                        }}
                        className={`bg-[#131f490f] w-[12rem] xl:w-[11rem] h-[2rem] 2xl:h-[2.5rem] px-4 py-1 text-[12px] rounded items-center justify-center flex gap-x-3 cursor-pointer ${
                          viewPage == "conversation"
                            ? "border-b-4 border-b-[#E98A3C] text-[#E98A3C]"
                            : "text-[#535BA4] border-b-2"
                        }`}
                      >
                        <img
                          loading="lazy"
                          src={
                            viewPage == "conversation"
                              ? "./LearnBotConversation_select.svg"
                              : "./LearnBotConversation.svg"
                          }
                          alt="BotConversation"
                        />
                        Bot Conversation
                      </button>
                      <button
                        onClick={() => {
                          if (audioRef.current) {
                            audioRef.current.pause();
                            audioRef.current.currentTime = 0; // Reset to the beginning
                            console.log("Audio stopped");
                          }
                          setAudioReload(false);
                          setMic(false);
                          setViewPage("video");
                        }}
                        className={`bg-[#131f490f] w-[12rem] xl:w-[11rem] h-[2rem] 2xl:h-[2.5rem] px-4 py-1 text-[12px] rounded items-center justify-center flex gap-x-3 cursor-pointer ${
                          viewPage == "video"
                            ? "border-b-4 border-b-[#E98A3C] text-[#E98A3C]"
                            : "text-[#535BA4] border-b-2"
                        }`}
                      >
                        <img
                          loading="lazy"
                          src={
                            viewPage == "video"
                              ? "./LearnVideo_select.svg"
                              : "./LearnVideo.svg"
                          }
                          alt="LearnVideo"
                        />
                        Video
                      </button>
                      <button
                        onClick={() => {
                          if (audioRef.current) {
                            audioRef.current.pause();
                            audioRef.current.currentTime = 0; // Reset to the beginning
                            console.log("Audio stopped");
                          }
                          setAudioReload(false);
                          setMic(false);
                          setViewPage("document");
                        }}
                        className={`bg-[#131f490f] w-[12rem] xl:w-[11rem] h-[2rem] 2xl:h-[2.5rem] px-4 py-1 text-[12px] rounded items-center justify-center flex gap-x-3 cursor-pointer ${
                          viewPage == "document"
                            ? "border-b-4 border-b-[#E98A3C] text-[#E98A3C]"
                            : "text-[#535BA4] border-b-2"
                        }`}
                      >
                        <img
                          loading="lazy"
                          src={
                            viewPage == "document"
                              ? "./LearnPDF_select.svg"
                              : "./LearnPDF.svg"
                          }
                          alt="LearnPDF"
                        />
                        Document
                      </button>
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                {/* Main Container */}
                {/* Conversation Container */}
                {viewPage == "conversation" &&
                  environment &&
                  avatar &&
                  language &&
                  voice && (
                    // layout && (
                    <ConversationLayout1
                      isThinking={isThinking}
                      layout={layout}
                      environment={environment}
                      avatar={{ selected: avatars }}
                      avatarAction={avatarAction}
                      audioReload={audioReload}
                      recording={recording}
                      mode={mode}
                      finalConversationHistory={finalConversationHistory}
                      language={language}
                      setMic={setMic}
                      mic={mic}
                      voice={voice}
                      setRecording={setRecording}
                      startRecording={startRecording}
                      audioStream={audioStream}
                      stopRecording={stopRecording}
                      userInput={userInput}
                      setUserInput={setUserInput}
                      sendMessage={sendMessage}
                      finishButton={finishButton}
                      SkipTTS={SkipTTS}
                      audioRef={audioRef}
                    />
                  )}
                {/* Video Container */}
                {viewPage == "video" && <LearnModeVideo />}
                {/* Document Container */}
                {viewPage == "document" && <LearnModeDocument />}
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-end items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  {/* <button
                    onClick={() =>
                      navigate("/assigned-course", { replace: true })
                    }
                    className="h-auto w-[10rem] xl:w-[12rem] 2xl:w-[13rem] border border-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#F68D1E] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                  >
                    <img src="./leftarrow.svg" alt="LeftArrow" />
                    back
                  </button> */}
                  <FinishConversationButtons
                    audioRef={audioRef}
                    setMic={setMic}
                    setAudioReload={setAudioReload}
                    setConversationHistory={setConversationHistory}
                    disable={true}
                    // disable={
                    //   conversationHistory.length > 3 && !mic ? true : false
                    // }
                    mode={"learn"}
                    setFinishButton={setFinishButton}
                  />
                </div>
              </div>
              <div
                className={`transition-all duration-700 ease-in-out h-full 
                  w-[20rem]
                bg-[#FFFFFF8F] inset-shadow-sm inset-shadow-[#ffffff] rounded-r-[10px] cursor-default`}
              >
                <AssignSideMenu index={5} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearnModeConversation;
