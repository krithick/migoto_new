import React, { useEffect, useRef, useState } from "react";
import HeaderMenu from "./components/HeaderMenu";
import AssignSideMenu from "./components/AssignSideMenu";
import { useNavigate } from "react-router";
import { Canvas } from "@react-three/fiber";
import LightHelper from "./components/LightHelper";
import CharacterLoader from "./components/CharacterLoader";
import EvaluationConversation from "./components/EvaluationConversation";
import TryConversation from "./components/TryConversation";
import axios from "axios";
import toast from "react-hot-toast";
import RecordRTC from "recordrtc";
import { Visualizer } from "react-sound-visualizer";
import FinishConversationButtons from "./components/FinishConversationButtons";
import ModelAnimationLoader from "./components/ModelAnimationLoader";
import { Baseurl } from "./route";

const Conversation = () => {
  const animationGLB = "/Character/Moh_Armature.glb";

  // "/Character/Moh_Glass_Gls1.glb",
  const glbfiles = [
    "/Character/Moh_Beard_Br1.glb",
    "/Character/Moh_Body_B1.glb",
    "/Character/Moh_Hair_Hr1.glb",
    "/Character/Moh_Pant_Pt1.glb",
    "/Character/Moh_Shirt_St1.glb",
  ];
  const [course, setCourse] = useState(null);
  const [avatar, setAvatar] = useState(null);
  const [language, setLanguage] = useState(null);
  const [voice, setVoice] = useState(null);
  const [mode, setMode] = useState(null);
  // UseState for when the user using mic to recording input speech.
  const [recording, setRecording] = useState(false);
  // UseState for Page referesh.
  const [pageReload, setPageReload] = useState(false);
  // UseState for store user and AI bot conversation
  const [conversationHistory, setConversationHistory] = useState([]);
  // UseState for store chat session ID.
  const [sessionID, setSessionID] = useState(null);
  // UseState for store AI avatar animation.
  const [avatarAction, setAvatarAction] = useState("Neutral");
  // UseState for handle with finish button disable function
  const [finishButton, setFinishButton] = useState(false);
  const [mic, setMic] = useState(false);
  const [audioStream, setAudioStream] = useState(null);
  // UseRef for user audio input validation.
  const recorderRef = useRef(null);
  // UseState for bot audio playing or not.
  const [audioReload, setAudioReload] = useState(false);
  const [botResponse, setBotResponce] = useState(null);
  const [userInput, setUserInput] = useState("");
  const audioRef = useRef(new Audio());

  // Save conversation Start time
  const [startTotalDurationTime, setStartTotalDurationTime] = useState(null);
  // Save overal duration in conversation
  // State variables
  const [startAverageDurationTime, setStartAverageDurationTime] =
    useState(null);
  const [intervals, setIntervals] = useState([]);
  useEffect(() => {
    if (localStorage.getItem("migoto-course") != null) {
      setCourse(JSON.parse(localStorage.getItem("migoto-course")));
    }
    if (localStorage.getItem("migoto-avatar") != null) {
      setAvatar(JSON.parse(localStorage.getItem("migoto-avatar")));
    }
    if (localStorage.getItem("migoto-mode") != null) {
      setMode(JSON.parse(localStorage.getItem("migoto-mode")));
    }
    if (localStorage.getItem("migoto-language") != null) {
      setLanguage(JSON.parse(localStorage.getItem("migoto-language")));
    }
    if (localStorage.getItem("migoto-voice") != null) {
      setVoice(JSON.parse(localStorage.getItem("migoto-voice")));
    }
  }, []);

  let navigate = useNavigate();
  const NavigateFunction = () => {
    navigate("/report", { replace: true });
  };

  // Function to get the current time in hh:mm:ss format
  const getFormattedTime = () => {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");
    return `${hours}:${minutes}:${seconds}`;
  };

  // User Start recording
  const startRecording = async () => {
    try {
      if (finishButton == true) {
        toast.error("Your conversation has ended.");
      } else {
        setUserInput("");
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        setAudioStream(stream);
        recorderRef.current = new RecordRTC(stream, {
          type: "audio",
          mimeType: "audio/wav",
          recorderType: RecordRTC.StereoAudioRecorder,
          desiredSampRate: 16000,
        });
        recorderRef.current.startRecording();
        setRecording(true);
        if (conversationHistory.length == 0) {
          const start = new Date().getTime(); // Get current time in milliseconds
          setStartTotalDurationTime(start);
        }
      }
    } catch (error) {
      console.error("Error accessing microphone", error);
      toast.error("Microphone not available...");
    }
  };

  // User Stop recording
  const stopRecording = () => {
    setUserInput("");
    recorderRef.current.stopRecording(() => {
      const blob = recorderRef.current.getBlob();
      // calling to wit.ai dictation api for speech to text (STT).
      Request_to_witAI_for_SST(blob);
      // STT_Gemini(blob);
    });
    setRecording(false);
    setMic(true);
  };

  // Post audio to Wit.ai API
  const Request_to_witAI_for_SST = async (props) => {
    const formData = new FormData();
    formData.append("file", props, "audio.wav");
    // formData.append("language", "english");
    formData.append("language", language.title.toLowerCase());

    const apiUrl = `${Baseurl}stt`;

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        // headers: {
        //   // Authorization: `Bearer ${token}`,
        //   "Content-Type": "audio/wav", // Ensure that we set the content-type correctly
        // },
        body: formData, // Directly pass the Blob as body
      });

      if (!response.ok) {
        throw new Error("Failed to send audio to Wit.ai");
      }

      const data = await response.text();
      let responceText = await JSON.parse(data);
      if (responceText?.text != "") {
        // setConversationHistory((x) => [
        //   ...x,
        //   {
        //     role: "user",
        //     // correct: false,
        //     message: responceText?.text,
        //   },
        // ]);

        setPageReload(!pageReload);
        // Calling chat API to upload user voice text.
        Request_to_Gemini(responceText?.text);
        // Stop Overal time and Save interval
        if (conversationHistory.length >= 1) {
          // setEndAverageDurationTime(getFormattedTime());
          const start = new Date(`1970-01-01T${startAverageDurationTime}Z`);
          const end = new Date(`1970-01-01T${getFormattedTime()}Z`);
          const interval = (end - start) / 1000; // Time difference in seconds
          setIntervals((prevIntervals) => [...prevIntervals, interval]);
        }
      } else {
        // Incause user send empty vioce, show the error message via toast.
        toast.error("Couldn't hear you. Please try again!");
        setMic(false);
      }
    } catch (error) {
      console.error("Error posting to Speak to Text:", error);
    }
  };

  // Implement Chat API
  const Request_to_Gemini = async (message) => {
    setRecording(false);
    setMic(true);
    setConversationHistory((x) => [
      ...x,
      {
        role: "user",
        // correct: false,
        message: message,
      },
    ]);
    //
    if (message != "") {
      // Replacement for Canada to Canara
      let formData = new FormData();

      if (sessionID == null) {
        if (mode?.title !== "Try Mode") {
          if (language?.title.toLowerCase() == "english") {
            formData.append(
              "scenario_name",
              "PNB Pragati Current account_train"
            );
          } else {
            formData.append(
              "scenario_name",
              "PNB Pragati Current account_train_hindi"
            );
          }
        } else {
          if (language.name == "english") {
            formData.append("scenario_name", mode?.scenario);
          } else {
            formData.append("scenario_name", `${mode?.scenario}_hindi`);
          }
        }
        formData.append("message", message);
        formData.append("name", avatar?.name);
      } else {
        formData.append("session_id", sessionID);
        formData.append("message", message);
        formData.append("name", avatar?.title);
      }
      const headers = {
        "Content-type": "multipart/form-data",
        Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
      };
      // Calling Chat API and post data.
      await axios
        .post(`${Baseurl}chat`, formData, { headers })

        // API success message.
        .then((res) => {
          // Store session id for in this conversation.
          setSessionID(res.data.session_id);
          localStorage.setItem("sessionID", res.data.session_id);
          const eventSource = new EventSource(
            `${Baseurl}chat/stream?session_id=${res.data.session_id}&name=${avatar?.title}`,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem("migoto-token")}`,
              },
            }
          );

          let bot;

          eventSource.onmessage = (event) => {
            let mess = JSON.parse(event.data);
            bot = mess;
          };

          eventSource.onerror = () => {
            // setUserInput(null);
            if (mode?.name == "Training Mode") {
              if (bot?.correct == true) {
                Request_to_WitAI_for_TTS(bot);
                setBotResponce(bot.response);
              } else {
                setConversationHistory((x) => [
                  ...x,
                  {
                    role: "bot",
                    message: bot.correct_answer,
                    correct: bot.correct,
                  },
                ]);

                setBotResponce(bot.response);
                setPageReload(!pageReload);
                setAudioReload(false);
                if (bot?.complete == true) {
                  setFinishButton(true);
                }
              }
            } else {
              Request_to_WitAI_for_TTS(bot);
              setBotResponce(bot.response);
            }
            if (bot?.emotion != "") {
              // Store AI avatar emotions.
              setAvatarAction(bot?.emotion);
            }
            // console.log("res.data.response: ", bot);

            console.error("EventSource error, closing connection.");
            eventSource.close();
          };
          // Page reload state.
          setPageReload(!pageReload);
        })
        // API error message.
        .catch((err) => {
          console.log("err: ", err);
          setMic(false);
          // API throw error message then show user via toast.
        });
    }
  };

  // Function to handle text-to-speech request
  const Request_to_WitAI_for_TTS = async (props) => {
    const apiUrl =
       ";

    const ssml = `
    <speak version='1.0' xml:lang='en-IN'>
      <voice xml:lang='en-US' xml:gender="Male" name='${
        language?.title == "english" ? voice?.voice : voice?.voice
      }'>
        ${props?.response}
      </voice>
    </speak>`;

    try {
      // Sending the POST request to Wit.ai API
      const response = await axios.post(apiUrl, ssml, {
       
      });

      // The response body contains the audio in MPEG format (MP3)
      const audioBlob = new Blob([response.data], { type: "audio/wav" });
      const AUDIOURL = URL.createObjectURL(audioBlob);

      audioRef.current.src = AUDIOURL;

      setAudioReload(true);
      // const tmp = new Audio(AUDIOURL); //passing your state (hook)
      audioRef.current.play().catch((error) => console.error(error));
      // tmp.play().catch((error) => console.error(error));

      audioRef.current.onplay = () => {
        console.log("Audio started playing.");
        // Handle when audio starts
        setAudioReload(true); // Could show loading state or UI updates here
      };

      audioRef.current.onended = () => {
        console.log("Audio playback completed.");

        if (props?.complete == true) {
          setFinishButton(true);
        }

        // Push to conversation for bot responce and save.

        setConversationHistory((x) => [
          ...x,
          {
            role: "bot",
            message: props?.response,
            correct: props?.correct,
          },
        ]);
        setUserInput("");

        // Handle when audio finishes playing
        setAudioReload(false); // Could hide loading state or trigger other actions here
        if (props?.complete == true) {
          setMic(true);
        } else {
          setMic(false);
        }
        // Start Overal time
        if (conversationHistory.length >= 1) {
          setStartAverageDurationTime(getFormattedTime());
        }
        audioRef.current = new Audio();
      };

      // Set the audio URL to be played
      // setAudioUrl(audioUrl);
    } catch (err) {
      console.error("Error with Wit.ai Text-to-Speech request:", err);
      // setError(err.message);
    } finally {
      console.log("Mic Off");
      setAudioReload(false);
      // audioRef.current = null;
    }
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
        <HeaderMenu />
        <div className="h-[35.5rem] xl:h-[35.5rem] 2xl:h-[56rem] w-screen flex items-center">
          <div className="h-full w-screen place-content-center px-[10rem] xl:px-[7.5rem] 2xl:px-[10rem] pb-[5rem]">
            <div className="h-[50px] xl:h-[40px] 2xl:h-[50px] flex items-center text-[#000000] text-[16px] xl:text-[14px] 2xl:text-[16px] font-medium">
              Assigned Courses
            </div>
            <div className="h-full w-full bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px] flex">
              <div className="h-full w-[80rem]">
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <div className="flex flex-auto justify-start">
                    <div className="flex items-center space-x-[10px]">
                      <span className="text-[16px] xl:text-[14px] 2xl:text-[16px] text-[#131F49]">
                        {course?.title}
                      </span>
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[40.8rem] xl:h-[24rem] 2xl:h-[40.8rem] w-full px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem] py-[15px] xl:py-[10px] 2xl:py-[15px]">
                  <div className="h-full w-full flex justify-center items-center gap-x-[5rem] xl:gap-x-[2.5rem] 2xl:gap-x-[5rem] overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                    {/* Conversation */}
                    <div className="h-[35rem] xl:h-[22.5rem] 2xl:h-[35rem] w-[25rem] xl:w-[17rem] 2xl:w-[25rem] bg-[#FFFFFF8F]">
                      <div className="h-[3rem] xl:h-[2.5rem] 2xl:h-[3rem] w-full flex justify-start items-center bg-[#131F49] text-[#FFFFFF] text-[16px] xl:text-[14px] 2xl:text-[16px] rounded-t-[10px] px-5">
                        {avatar?.title}
                      </div>
                      <div className="h-[28rem] xl:h-[21.5rem] 2xl:h-[32rem] w-full relative">
                        <div className="absolute inset-0 h-full w-full">
                          <img
                            loading="lazy"
                            src="./sample_BG.png"
                            alt=""
                            className="h-full w-full object-fill"
                          />
                        </div>
                        <Canvas
                          className="h-full w-full"
                          camera={{
                            fov: 55,
                            far: 100,
                            position: [0, 10, 10],
                            rotation: [-0, 0, 0],
                          }}
                        >
                          <LightHelper />
                          <ModelAnimationLoader
                            recording={recording}
                            avatarAction={avatarAction}
                            audioReload={audioReload}
                            animationGLB={animationGLB}
                            glbfiles={glbfiles}
                            // // animationGLB={avatar?.glbfiles}
                            // glbfiles={avatar?.glbfiles}
                          />
                        </Canvas>
                      </div>
                    </div>
                    <div className="h-[35rem] xl:h-[22.5rem] 2xl:h-[35rem] w-[25rem] xl:w-[17rem] 2xl:w-[25rem] bg-[#FFFFFF8F]">
                      <div className="h-[3rem] xl:h-[2.5rem] 2xl:h-[3rem] w-full flex justify-start items-center bg-[#131F49] text-[#FFFFFF] text-[16px] xl:text-[14px] rounded-t-[10px] px-5">
                        Conversation
                      </div>
                      <div className="h-[28rem] xl:h-[16rem] 2xl:h-[28rem] w-full flex justify-center items-center pr-2 py-1.5">
                        {/* Conversation Dialog */}
                        {mode?.title == "Try Mode" ? (
                          <EvaluationConversation
                            conversation={conversationHistory}
                            avatar={avatar?.title}
                            finish={finishButton}
                            language={language?.title}
                          />
                        ) : (
                          <TryConversation
                            conversation={conversationHistory}
                            language={language}
                            setMic={setMic}
                            avatar={avatar?.name}
                            finish={finishButton}
                          />
                        )}
                      </div>
                      <div className="h-[4rem] w-full bg-[#131f4998] rounded-b-[10px] flex justify-between items-center px-3.5 py-1">
                        <div className="text-center -space-y-1.5">
                          <div
                            className={`h-8 w-8 ${
                              !mic
                                ? "bg-[#131F49] text-white cursor-pointer"
                                : "bg-[#9599a7b0] text-[#ffffff7c]"
                            } flex justify-center items-center rounded-full `}
                          >
                            <img
                              loading="lazy"
                              src={
                                recording ? "./close_white.svg" : "./speak.svg"
                              }
                              alt="speak"
                              className={`h-full w-full ${
                                recording ? "p-2" : "p-1"
                              }`}
                              onClick={() => {
                                if (recording) {
                                  setRecording(false);
                                  recorderRef.current = null;
                                } else {
                                  startRecording();
                                }
                              }}
                            />
                          </div>
                          <span className="text-[#FFFFFF] text-[8px]">
                            {recording ? "Cancel" : "Speak"}
                          </span>
                        </div>
                        <div>
                          {recording ? (
                            <Visualizer
                              audio={audioStream}
                              mode={"continuous"}
                              autoStart={true}
                              strokeColor={"#131F49"}
                            >
                              {({ canvasRef }) => (
                                <>
                                  <canvas
                                    ref={canvasRef}
                                    className="h-12 xl:h-9 3xl:h-12 3xl:w-96 w-60 xl:w-40 2xl:w-64 bg-[#f2f2f22f] rounded"
                                  />
                                </>
                              )}
                            </Visualizer>
                          ) : (
                            <input
                              disabled={mic}
                              type="text"
                              value={userInput}
                              onChange={(e) => setUserInput(e.target.value)}
                              placeholder="Type Here"
                              className="w-60 xl:w-40 2xl:w-64 h-auto py-2 px-1.5 bg-[#C7DFF09C] rounded-[5px] text-[12px] font-600 focus:outline-none text-[#131F49]"
                            />
                          )}
                        </div>
                        <div className="text-center -space-y-1.5">
                          <div
                            className={`h-8 w-8 flex justify-center items-center rounded-full ${
                              !mic
                                ? "bg-[#FFFFFF] text-[#F68D1E] cursor-pointer"
                                : "bg-[#9599a7b0] text-[#ffffff7c]"
                            }`}
                          >
                            <img
                              loading="lazy"
                              src="./send.svg"
                              alt="send"
                              className="h-full w-full p-2"
                              onClick={() => {
                                if (userInput != null) {
                                  Request_to_Gemini(userInput);
                                } else {
                                  if (!mic && recorderRef.current != null)
                                    stopRecording();
                                  else toast.error("No Input");
                                }
                              }}
                            />
                          </div>
                          <span className="text-[#FFFFFF] text-[8px]">
                            Send
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-end items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  {mode?.title !== "Evaluate Mode" ? (
                    <FinishConversationButtons mode={mode?.title} />
                  ) : (
                    //  <button
                    //     onClick={() => navigate("/confirmation")}
                    //     className="h-auto w-[10rem] xl:w-[8rem] 2xl:w-[10rem] border border-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#F68D1E] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                    //   >
                    //     <img src="./leftarrow.svg" alt="LeftArrow" />
                    //     back
                    //   </button>
                    <button
                      onClick={() => NavigateFunction()}
                      className="h-auto w-[10rem] xl:w-[10rem] 2xl:w-[12rem] bg-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#FFFFFF] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                    >
                      Generate Report
                      <img
                        src="./rightarrow.svg"
                        alt="RightArrow"
                        loading="lazy"
                      />
                    </button>
                  )}
                </div>
              </div>
              <div
                className={`transition-all duration-700 ease-in-out h-full 
                  w-[20rem]
                bg-[#FFFFFF8F] inset-shadow-sm inset-shadow-[#ffffff] rounded-r-[10px] cursor-default`}
              >
                <AssignSideMenu index={11} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Conversation;
