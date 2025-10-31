// Importing necessary libraries and components
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import HeaderMenu from "./components/HeaderMenu";
import AssignSideMenu from "./components/AssignSideMenu";
import FinishConversationButtons from "./components/FinishConversationButtons";

import toast from "react-hot-toast";
import useSTT from "./hooks/useSTT";
import useTTS from "./hooks/useTTS";
import useLLM from "./hooks/useLLM";
import ConversationLayout1 from "./components/ConversationLayout1";
import ConversationLayout3 from "./components/ConversationLayout3";
import ConversationLayout4 from "./components/ConversationLayout4";
import ConversationLayout2 from "./components/ConversationLayout2";
import instance from "./service";
import CoachVideoPlayer from "./components/CoachVideoPlayer";
import ViewReportModel from "./components/ViewReportModel";
import ReportCard from "./components/ReportCard";

// Main functional component for the conversation hook
const ConversationHook = () => {
  // React Router's navigation hook
  const navigate = useNavigate();

  // State variables for managing various aspects of the component
  const [isThinking, setIsThinking] = useState(false);
  const [reportModelView, setReportModelView] = useState(false);
  const [viewModel, setViewModel] = useState("report");
  const [close, setClose] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [coachMessage, setCoachMessage] = useState(null);
  const [language, setLanguage] = useState(null);
  const [recording, setRecording] = useState(false);
  const [reload, setReload] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [voice, setVoice] = useState(null);
  const [environment, setEnvironment] = useState(null);
  const [course, setCourse] = useState(null);
  const [avatar, setAvatar] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [mode, setMode] = useState(null);
  const [pageReload, setPageReload] = useState(false);
  const [finishButton, setFinishButton] = useState(false);
  const [mic, setMic] = useState(false);
  const [audioReload, setAudioReload] = useState(false);
  const [loading, setLoading] = useState(false);
  const [avatarAction, setAvatarAction] = useState("Neutral");
  const [userInput, setUserInput] = useState("");
  const [startTotalDurationTime, setStartTotalDurationTime] = useState(null);
  const [startAverageDurationTime, setStartAverageDurationTime] =
    useState(null);
  const [intervals, setIntervals] = useState([]);
  // console.log("intervals: ", intervals);
  // console.log("startTotalDurationTime: ", startTotalDurationTime);
  // console.log("startAverageDurationTime: ", startAverageDurationTime);

  // Fetching user-selected data from local storage on component mount
  useEffect(() => {
    if (localStorage.getItem("migoto-token") == null) {
      navigate("/login", { replace: true });
    }
    if (localStorage.getItem("migoto-course")) {
      setCourse(JSON.parse(localStorage.getItem("migoto-course")));
    }
    if (localStorage.getItem("migoto-avatar")) {
      setAvatar(JSON.parse(localStorage.getItem("migoto-avatar")));
    }
    if (localStorage.getItem("migoto-scenario")) {
      setScenario(JSON.parse(localStorage.getItem("migoto-scenario")));
    }
    if (localStorage.getItem("migoto-mode")) {
      setMode(JSON.parse(localStorage.getItem("migoto-mode")));
    }
    if (localStorage.getItem("migoto-language")) {
      setLanguage(JSON.parse(localStorage.getItem("migoto-language")));
    }
    if (localStorage.getItem("migoto-voice")) {
      setVoice(JSON.parse(localStorage.getItem("migoto-voice")));
    }
    if (localStorage.getItem("migoto-environment")) {
      setEnvironment(JSON.parse(localStorage.getItem("migoto-environment")));
    }
  }, []);

  // useEffect(() => {
  //   setTimeout(() => {
  //     sendMessage("hi");
  //   }, 3000);
  // }, []);

  // Function to get the current time in hh:mm:ss format
  const getFormattedTime = () => {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");
    return `${hours}:${minutes}:${seconds}`;
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
      setIsThinking(true);
    } else {
      toast.error("Couldn't hear you. Please try again!");
    }
  };

  // Handler for processing bot responses
  const handleBotResponse = (bot) => {
    if (bot?.emotion) setAvatarAction(bot.emotion);
    if (bot?.correct !== undefined) {
      if (bot?.correct == true && mode?.title == "Try Mode") {
        setIsThinking(false); // Hide thinking when TTS starts
        speak(bot.audio, bot.correct, bot.complete);
      } else if (mode?.title == "Assess Mode") {
        setIsThinking(false); // Hide thinking when TTS starts
        speak(bot.audio, bot.correct, bot.complete);
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
    // Start Overal time
    if (conversationHistory.length >= 0) {
      setStartAverageDurationTime(getFormattedTime());
    }
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
    sessionId,
    setCoachMessage,
    setIsThinking
  );

  const sendMessage = (message) => {
    setIsThinking(true);
    llmSendMessage(message);
  };

  // Function to navigate to the report page
  const NavigateFunction = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0; // Reset to the beginning
      console.log("Audio stopped");
    }
    const end = new Date().getTime(); // Get current time in milliseconds
    // Calculate Total duration in one particular conversation
    const difference = end - startTotalDurationTime;

    const hours = Math.floor(difference / 1000 / 60 / 60);
    const minutes = Math.floor((difference / 1000 / 60) % 60);
    const seconds = Math.floor((difference / 1000) % 60);

    let Total_Conversation_Time = `${hours
      .toString()
      .padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds
      .toString()
      .padStart(2, "0")}`;
    // Calculate Avarage time duration
    const sum = intervals.reduce((acc, interval) => acc + interval, 0);
    const avg = sum / intervals.length;
    const avgHours = Math.floor(avg / 3600);
    const avgMinutes = Math.floor((avg % 3600) / 60);
    const avgSeconds = Math.round(avg % 60);
    let Average_Conversation_Time = `${avgHours
      .toString()
      .padStart(2, "0")}:${avgMinutes.toString().padStart(2, "0")}:${avgSeconds
      .toString()
      .padStart(2, "0")}`;
    setLoading(true);
    const headers = {
      "Content-Type": "multipart/form-data",
      Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
    };

    instance
      .put(
        `/scenario-assignments/me/scenario/${scenario?.id}/mode/assess_mode/complete`,
        null,
        { headers }
      )
      .then((responce) => {
        setLoading(false);
        setViewModel("report");
        setReportModelView(!reportModelView);
        setReload(!reload);
        // localStorage.setItem("migoto-url", "/report");
        // navigate("/report", { replace: true });
      })
      .catch((error) => {
        setLoading(false);
        console.log("Error update complete scenario and modes : ", error);
        toast.error("try again");
      });
  };

  // useEffect(() => {
  //   window.addEventListener("keypress", (event) => {
  //     ChangeAvatar(event.key);
  //   });
  //   return window.removeEventListener("keypress", (event) => {
  //     ChangeAvatar(event.key);
  //   });
  // }, []);

  // const ChangeAvatar = (props) => {
  //   if (props == "Enter") {
  //     console.log("props: ", props);
  //     console.log("userInput: ", userInput);
  //     if (userInput.trim()) {
  //       sendMessage(userInput);
  //       setMic(true);
  //       setUserInput("");
  //     } else {
  //       if (!mic && !finishButton && recording) stopRecording();
  //       else if (finishButton) toast.error("Finish Conversation");
  //       else toast.error("No Input");
  //     }
  //   }
  // };

  // const handlePopState = () => {
  //   if (audioRef.current) {
  //     console.log("audioRef: ", audioRef);
  //     audioRef.current.pause();
  //     audioRef.current.currentTime = 0; // Reset to the beginning
  //     console.log("Audio stopped");
  //   }
  // };

  // useEffect(() => {
  //   window.addEventListener("popstate", handlePopState);

  //   return () => {
  //     window.removeEventListener("popstate", handlePopState);
  //   };
  // }, []);

  // JSX structure for rendering the component
  return (
    <div className="absolute inset-0 backdrop-blur-[68px]">
      <div className="h-screen w-screen relative">
        {/* Header menu */}
        <HeaderMenu
          audioRef={audioRef}
          index={"1"}
          disable={
            conversationHistory.length == 0 || finishButton ? true : false
          }
          reload={reload}
          setReload={setReload}
        />
        <div className="h-[35.5rem] xl:h-[35.5rem] 2xl:h-[54rem] w-screen flex items-center">
          <div className="h-full w-screen place-content-center px-[10rem] xl:px-[7.5rem] 2xl:px-[10rem] pb-[5rem]">
            <div className="h-[50px] flex items-center text-[#000000] text-[16px] font-medium">
              Assigned Courses
            </div>
            <div className="h-full w-full bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px] flex">
              {/* Left Section */}
              <div
                className={`transition-all duration-700 ease-in-out animate-fade-left animate-ease-linear h-full w-[80rem] ${
                  close
                    ? "xl:w-[70rem] 2xl:w-[100rem]"
                    : "xl:w-[55.5rem] 2xl:w-[80rem]"
                }`}
              >
                {/* Top Bar */}
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex items-center px-[3.5rem]">
                  <div className="flex flex-auto justify-start">
                    <div className="flex flex-auto items-center space-x-[10px]">
                      <span className="text-[16px] xl:text-[14px] 2xl:text-[16px] text-[#131F49]">
                        {course?.title}
                      </span>
                    </div>
                    {close && (
                      <div className="has-tooltip">
                        <span className="tooltip p-1 mt-6 text-[12px] rounded bg-[#131f4928] border border-[#FFFFFF]">
                          Progress Bar
                        </span>
                        <img
                          onClick={() => setClose(false)}
                          loading="lazy"
                          src="./menu.svg"
                          alt="menu"
                          className="bg-[#131f4928] border border-[#FFFFFF] p-1.5 cursor-pointer"
                        />
                      </div>
                    )}
                  </div>
                </div>

                <hr className="mx-[3.5rem] text-[#131f4946] h-0" />
                {/* Main Content */}
                {environment && environment.layout == "1" && (
                  <ConversationLayout1
                    isThinking={isThinking}
                    environment={environment}
                    avatar={avatar}
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
                    setCoachMessage={setCoachMessage}
                    SkipTTS={SkipTTS}
                    audioRef={audioRef}
                  />
                )}

                {environment && environment.layout == "2" && (
                  <ConversationLayout2
                    isThinking={isThinking}
                    environment={environment}
                    avatar={avatar}
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
                    close={close}
                    setCoachMessage={setCoachMessage}
                    SkipTTS={SkipTTS}
                    audioRef={audioRef}
                  />
                )}

                {environment && environment.layout == "3" && (
                  <ConversationLayout3
                    isThinking={isThinking}
                    environment={environment}
                    avatar={avatar}
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
                    setCoachMessage={setCoachMessage}
                    SkipTTS={SkipTTS}
                    audioRef={audioRef}
                  />
                )}

                {environment && environment.layout == "4" && (
                  <ConversationLayout4
                    isThinking={isThinking}
                    environment={environment}
                    avatar={avatar}
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
                    setCoachMessage={setCoachMessage}
                    SkipTTS={SkipTTS}
                    audioRef={audioRef}
                  />
                )}

                <hr className="mx-[3.5rem] text-[#131f4946] h-0" />

                {/* Bottom Button */}
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-between items-center px-[3.5rem]">
                  <div className="flex space-x-5">
                    <button
                      onClick={() => {
                        if (audioRef.current) {
                          audioRef.current.pause();
                          audioRef.current.currentTime = 0; // Reset to the beginning
                        }
                        localStorage.setItem("migoto-url", "/confirmation");
                        navigate("/confirmation", { replace: true });
                      }}
                      className="h-auto w-[10rem] xl:w-[8rem] 2xl:w-[10rem] border border-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#F68D1E] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                    >
                      <img
                        src="./leftarrow.svg"
                        alt="LeftArrow"
                        loading="lazy"
                      />
                      back
                    </button>
                    {mode?.title == "Assess Mode" && (
                      <button
                        onClick={() => {
                          if (audioRef.current) {
                            audioRef.current.pause();
                            audioRef.current.currentTime = 0; // Reset to the beginning
                            console.log("Audio stopped");
                          }
                          setConversationHistory([]);
                          setSessionId(null);
                        }}
                        className="h-auto w-[10rem] xl:w-[10rem] 2xl:w-[14rem] border border-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#F68D1E] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                      >
                        Restart Conversation
                      </button>
                    )}
                  </div>
                  {mode?.title != "Assess Mode" ? (
                    <FinishConversationButtons
                      audioRef={audioRef}
                      setMic={setMic}
                      setAudioReload={setAudioReload}
                      mode={mode?.title}
                      disable={
                        conversationHistory.length > 3 && !mic ? true : false
                      }
                      setConversationHistory={setConversationHistory}
                      conversationHistory={conversationHistory}
                      setFinishButton={setFinishButton}
                      setSessionId={setSessionId}
                    />
                  ) : (
                    <div className="flex space-x-3">
                      {/* Personalized Report Button */}
                      <button
                        onClick={() => {
                          if (conversationHistory.length > 3 && !mic) {
                            if (audioRef.current) {
                              audioRef.current.pause();
                              audioRef.current.currentTime = 0; // Reset to the beginning
                              console.log("Audio stopped");
                            }
                            setViewModel("personalize");
                            setReportModelView(!reportModelView);
                            setReload(!reload);
                            // localStorage.setItem(
                            //   "migoto-url",
                            //   "/personalized-report"
                            // );
                            // navigate("/personalized-report", { replace: true });
                          }
                        }}
                        disabled={conversationHistory.length > 3 && mic}
                        className={`h-auto w-[10rem] xl:w-[12rem] 2xl:w-[13rem] bg-[#F68D1E] flex justify-center items-center gap-2 py-1.5 text-[#FFFFFF] text-[18px] xl:text-[14px] 2xl:text-[16px] rounded-[5px] ${
                          conversationHistory.length > 3 && !mic
                            ? "bg-[#F68D1E] cursor-pointer"
                            : "bg-gray-300 cursor-default"
                        }`}
                      >
                        Personalized Report
                        <img
                          src="./courses.svg"
                          alt="ReportIcon"
                          loading="lazy"
                        />
                      </button>
                      {loading ? (
                        <button className="bg-[#F68D1E] h-auto w-[12rem] py-1 text-white text-[20px] xl:text-[16px] 2xl:text-[18px] flex justify-center items-center font-medium rounded-[10px] cursor-pointer">
                          <div role="status">
                            <svg
                              aria-hidden="true"
                              className="w-7 h-7 text-gray-200 animate-spin dark:text-gray-600 fill-[#597bd1]"
                              viewBox="0 0 100 101"
                              fill="none"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <path
                                d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                fill="currentColor"
                              />
                              <path
                                d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                fill="currentFill"
                              />
                            </svg>
                            <span className="sr-only">Loading...</span>
                          </div>
                        </button>
                      ) : (
                        <button
                          disabled={conversationHistory.length > 3 && mic}
                          onClick={() => {
                            if (conversationHistory.length > 3 && !mic)
                              NavigateFunction();
                          }}
                          className={`h-auto w-[10rem] xl:w-[12rem] 2xl:w-[13rem] bg-[#F68D1E] flex justify-center items-center gap-2 py-1.5 text-[#FFFFFF] text-[18px] xl:text-[14px] 2xl:text-[16px] rounded-[5px] ${
                            conversationHistory.length > 3 && !mic
                              ? "bg-[#F68D1E] cursor-pointer"
                              : "bg-gray-300 cursor-default"
                          }`}
                        >
                          Generate Report
                          <img
                            src="./rightarrow.svg"
                            alt="Arrow"
                            loading="lazy"
                          />
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Side Menu */}
              <div
                className={`transition-all duration-700 ease-in h-full ${
                  close ? "w-0" : "xl:w-[15rem] 2xl:w-[20rem]"
                } bg-[#FFFFFF8F] inset-shadow-sm inset-shadow-[#ffffff] rounded-r-[10px] cursor-default`}
              >
                <AssignSideMenu index={11} close={close} setClose={setClose} />
              </div>
            </div>
          </div>
        </div>

        <ReportCard
          reportModelView={reportModelView}
          setReportModelView={setReportModelView}
          viewModel={viewModel}
          scenarioName={scenario?.title}
          session_id={sessionId}
          reload={reload}
        />

        {/* Coach Video */}
        {coachMessage != null && (
          <CoachVideoPlayer
            message={coachMessage}
            setCoachMessage={setCoachMessage}
            setMic={setMic}
            voice={voice}
            avatar={avatar}
          />
        )}
      </div>
    </div>
  );
};

// Exporting the component as default
export default ConversationHook;
