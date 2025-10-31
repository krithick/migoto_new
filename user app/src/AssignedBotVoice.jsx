import React, { useEffect, useRef, useState } from "react";
import AssignSideMenu from "./components/AssignSideMenu";
import HeaderMenu from "./components/HeaderMenu";
import { useNavigate } from "react-router";
import { FaPlayCircle } from "react-icons/fa";
import { HiPauseCircle } from "react-icons/hi2";
import { Visualizer } from "react-sound-visualizer";
import toast from "react-hot-toast";
import instance from "./service";
import { useFormattedDate } from "./hooks/useFormattedDate";
// import BotVoice from "./components/BotVoice";

const AssignedBotVoice = () => {
  const [language, setLanguage] = useState(null);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("");
  const [reload, setReload] = useState(null);
  const [botvoiceDetails, setBotvoiceDetails] = useState(null);
  const [selectedTitle, setSelectedTitle] = useState(null);
  let navigate = useNavigate();

  const SelectionFunction = (props) => {
    if (selected == null) {
      setSelected(props);
    } else {
      if (selected.id == props.id) {
        setSelected(null);
      } else {
        setSelected(props);
      }
    }
  };

  const NavigateFunction = () => {
    if (selected != null) {
      localStorage.setItem(
        "migoto-voice",
        JSON.stringify({
          name: selected.name,
          language_code: selected.language_code,
          voice_id: selected.voice_id,
          voice_url: selected.voice_url,
          id: selected.id,
        })
      );
      localStorage.setItem("migoto-url", "/assigned-environment");
      navigate("/assigned-environment", { replace: true });
    } else {
      toast.error("Please select bot voice");
    }
  };

  const audioRef = useRef(new Audio());
  const [mediaStream, setMediaStream] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const generateTTS = async (props) => {
    // The response body contains the audio in MPEG format (MP3)
    // const AUDIOURL = props.voice_url;
    const response = await fetch(props.voice_url);
    const blob = await response.blob();
    extractStreamFromBlob(blob);
    audioRef.current.src = URL.createObjectURL(blob);
    audioRef.current.play().catch((error) => {
      setIsPlaying(false);
      console.error(error);
    });
    audioRef.current.onplay = () => {
      console.log("Audio started playing.");
      // Handle when audio starts
      setIsPlaying(true); // Could show loading state or UI updates here
    };
    audioRef.current.onended = () => {
      console.log("Audio playback completed.");
      // Handle when audio finishes playing
      setIsPlaying(false); // Could hide loading state or trigger other actions here
      audioRef.current = new Audio();
      setSelectedTitle(null);
      setMediaStream(null);
    };
  };

  // Convert Blob to MediaStream
  const extractStreamFromBlob = async (blob) => {
    const arrayBuffer = await blob.arrayBuffer();
    const audioContext = new AudioContext();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;

    const destination = audioContext.createMediaStreamDestination();
    source.connect(destination);
    source.start();

    const stream = destination.stream;
    setMediaStream(stream);
  };

  useEffect(() => {
    if (localStorage.getItem("migoto-token") == null) {
      navigate("/login", { replace: true });
    }

    if (localStorage.getItem("migoto-language") != null) {
      setLanguage(JSON.parse(localStorage.getItem("migoto-language")));
    }

    fetchAssignedAvatarDetails();
  }, [reload]);

  const fetchAssignedAvatarDetails = async () => {
    try {
      let avatarIntraction;
      if (localStorage.getItem("migoto-mode") != null) {
        avatarIntraction = JSON.parse(localStorage.getItem("migoto-mode"));
      }
      let language = JSON.parse(localStorage.getItem("migoto-language"));
      let avatar = JSON.parse(localStorage.getItem("migoto-avatar"));
      // Fetch and load token
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
      };
      instance
        .get(
          `/avatar-interactions/${avatarIntraction?.avatar_interaction}?expand=bot_voices`,
          {
            headers,
          }
        )
        .then((response) => {
          let voices = [];

          for (let i = 0; i < response.data.bot_voices.length; i++) {
            if (
              avatar?.selected.gender == response.data.bot_voices[i].gender &&
              language?.code == response.data.bot_voices[i].language_code
            )
              voices.push(response.data.bot_voices[i]);
          }
          setBotvoiceDetails(voices);
          if (localStorage.getItem("migoto-voice") != null) {
            let avatar_voice = JSON.parse(localStorage.getItem("migoto-voice"));
            if (avatar?.selected.gender == avatar_voice.gender) {
              setSelected(avatar_voice);
            } else {
              setSelected(voices[0]);
            }
          } else {
            setSelected(voices[0]);
          }
        })
        .catch((error) => {
          console.error("Error fetching assigned bot voices :", error);
        });
    } catch (error) {
      console.error("Error fetching assigned bot voices :", error);
    }
  };

  return (
    <div className="absolute inset-0 backdrop-blur-[68px]">
      <div className="h-screen w-screen relative">
        <HeaderMenu
          index={"1"}
          disable={true}
          reload={reload}
          setReload={setReload}
        />
        <div className="h-[35.5rem] xl:h-[35.5rem] 2xl:h-[54rem] w-screen flex items-center">
          <div className="h-full w-screen place-content-center px-[10rem] xl:px-[7.5rem] 2xl:px-[10rem] pb-[5rem]">
            <div className="h-[50px] xl:h-[40px] 2xl:h-[50px] flex items-center text-[#000000] text-[16px] xl:text-[14px] 2xl:text-[16px] font-medium">
              {language && language.name}
            </div>
            <div className="h-full w-full bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px] flex">
              <div className="h-full w-[80rem]">
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <div className="flex flex-auto justify-start">
                    <div>
                      <div className="flex items-center space-x-[10px]">
                        <img
                          src="./voice_current.svg"
                          alt="scenario"
                          loading="lazy"
                          className="h-auto w-auto xl:h-[14px] 2xl:h-auto object-contain"
                        />
                        <span className="text-[16px] xl:text-[14px] 2xl:text-[16px] text-[#131F49]">
                          Voice Selection
                        </span>
                      </div>
                      <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#131F49]">
                        Assigned Bot Voices:{" "}
                        {botvoiceDetails && botvoiceDetails.length}
                      </div>
                    </div>
                  </div>
                  <div className="relative w-[247px] xl:w-[175px] 2xl:w-[247px]">
                    <input
                      type="text"
                      placeholder="Search"
                      onChange={(e) => setFilter(e.target.value)}
                      className="w-full rounded-[30px] text-[10px] 2xl:text-[12px] text-[#000000] bg-[#C7DFF0] py-2 pr-4 pl-10 focus:outline-none"
                    />
                    <div className="absolute top-1/2 left-3 -translate-y-1/2 text-gray-400">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-[12px] xl:h-[14px] 2xl:h-[14px] w-5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1110.5 3a7.5 7.5 0 016.15 13.65z"
                        />
                      </svg>
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[40.8rem] xl:h-[24rem] 2xl:h-[39rem] w-full pl-[3.5rem] xl:pl-[2rem] 2xl:pl-[3.5rem] pr-[22px] xl:pr-[14px] 2xl:pr-[22px] py-[15px] xl:py-[10px] 2xl:py-[15px]">
                  <div className="h-full w-full flex flex-wrap gap-x-[5rem] xl:gap-x-[2.5rem] 2xl:gap-x-[5rem] -space-y-[50px] xl:space-y-[40px] 2xl:-space-y-[50px] overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                    {botvoiceDetails && botvoiceDetails?.length == 0 && (
                      <>
                        <div className="h-full w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] bg-[#FFFFFF8F] rounded-[10px] justify-center items-center">
                          No available voice, please contact to admin
                        </div>
                      </>
                    )}

                    {botvoiceDetails &&
                      botvoiceDetails.map((value, index) => (
                        <>
                          {filter != "" ? (
                            <>
                              {value.name.toLowerCase().includes(filter) ? (
                                <div
                                  key={index}
                                  className="h-[18rem] xl:h-[12rem] 2xl:h-[14rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px]"
                                >
                                  <div className="h-full w-full">
                                    <div className="h-[55%] xl:h-[60%] 2xl:h-[60%] w-full bg-[#e9e9e954] flex justify-center items-center">
                                      <div className="space-y-3.5">
                                        <div
                                          className="flex justify-center"
                                          onClick={() => {
                                            if (!isPlaying) {
                                              audioRef.current.pause();
                                              generateTTS(value);
                                              setSelectedTitle(value.name);
                                            } else {
                                              if (selectedTitle == value.name) {
                                                audioRef.current.pause();
                                                setSelectedTitle(null);
                                                setIsPlaying(false);
                                                setMediaStream(null);
                                              } else {
                                                audioRef.current.pause();
                                                setMediaStream(null);
                                                generateTTS(value);
                                                setSelectedTitle(value.name);
                                              }
                                            }
                                          }}
                                        >
                                          {isPlaying ? (
                                            <>
                                              {selectedTitle == value.name ? (
                                                <HiPauseCircle size={50} />
                                              ) : (
                                                <FaPlayCircle size={50} />
                                              )}
                                            </>
                                          ) : (
                                            <FaPlayCircle size={50} />
                                          )}
                                        </div>
                                        <div className="h-12 w-72 xl:h-9 xl:w-44 2xl:w-66 3xl:h-12 3xl:w-96 bg-[#F2F2F2]">
                                          {selectedTitle == value.name && (
                                            <Visualizer
                                              audio={mediaStream}
                                              mode={"continuous"}
                                              autoStart={true}
                                              strokeColor={"#000000"}
                                            >
                                              {({ canvasRef }) => (
                                                <>
                                                  <canvas
                                                    ref={canvasRef}
                                                    className="h-full w-full"
                                                  />
                                                </>
                                              )}
                                            </Visualizer>
                                          )}
                                        </div>
                                      </div>
                                    </div>
                                    <div className="h-[45%] w-full">
                                      <div className="h-[2rem] xl:h-[1rem] 2xl:h-[2rem] w-full space-y-0.5">
                                        <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                          {value.name}
                                        </div>
                                      </div>
                                      <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                                        <div className="w-full h-auto space-y-0.5">
                                          <div className="w-full h-auto flex text-[10px]">
                                            <div className="flex flex-auto text-[#0000008a]">
                                              {/* Assigned on:
                                                  {useFormattedDate(
                                                    value.assigned_date
                                                  )} */}
                                            </div>
                                            {/* <div
                                        className={`${
                                          value.completed
                                            ? "text-[#27A745]"
                                            : "text-[#A4A029]"
                                        }`}
                                      >
                                        {value.completed
                                          ? "Completed"
                                          : "Yet to Start"}
                                      </div> */}
                                          </div>
                                          <button
                                            onClick={() =>
                                              SelectionFunction(value)
                                            }
                                            className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                              selected?.id == value.id
                                                ? "bg-[#F68D1E] text-[#EEF8FB]"
                                                : "border border-[#F68D1E] text-[#F68D1E]"
                                            }`}
                                          >
                                            {selected?.id == value.id
                                              ? "Selected"
                                              : "Select"}
                                          </button>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              ) : null}
                            </>
                          ) : (
                            <div
                              key={index}
                              className="h-[18rem] xl:h-[12rem] 2xl:h-[14rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px]"
                            >
                              <div className="h-full w-full">
                                <div className="h-[55%] xl:h-[60%] 2xl:h-[60%] w-full bg-[#e9e9e954] flex justify-center items-center">
                                  <div className="space-y-3.5">
                                    <div
                                      className="flex justify-center"
                                      onClick={() => {
                                        if (!isPlaying) {
                                          audioRef.current.pause();
                                          generateTTS(value);
                                          setSelectedTitle(value.name);
                                        } else {
                                          if (selectedTitle == value.name) {
                                            audioRef.current.pause();
                                            setSelectedTitle(null);
                                            setIsPlaying(false);
                                            setMediaStream(null);
                                          } else {
                                            audioRef.current.pause();
                                            setMediaStream(null);
                                            generateTTS(value);
                                            setSelectedTitle(value.name);
                                          }
                                        }
                                      }}
                                    >
                                      {isPlaying ? (
                                        <>
                                          {selectedTitle == value.name ? (
                                            <HiPauseCircle size={50} />
                                          ) : (
                                            <FaPlayCircle size={50} />
                                          )}
                                        </>
                                      ) : (
                                        <FaPlayCircle size={50} />
                                      )}
                                    </div>
                                    <div className="h-12 w-72 xl:h-9 xl:w-44 2xl:w-66 3xl:h-12 3xl:w-96 bg-[#F2F2F2]">
                                      {selectedTitle == value.name && (
                                        <Visualizer
                                          audio={mediaStream}
                                          mode={"continuous"}
                                          autoStart={true}
                                          strokeColor={"#000000"}
                                        >
                                          {({ canvasRef }) => (
                                            <>
                                              <canvas
                                                ref={canvasRef}
                                                className="h-full w-full"
                                              />
                                            </>
                                          )}
                                        </Visualizer>
                                      )}
                                    </div>
                                  </div>
                                </div>
                                <div className="h-[45%] w-full">
                                  <div className="h-[2rem] xl:h-[1rem] 2xl:h-[2rem] w-full space-y-0.5">
                                    <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                      {value.name}
                                    </div>
                                  </div>
                                  <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                                    <div className="w-full h-auto space-y-0.5">
                                      <div className="w-full h-auto flex text-[10px]">
                                        <div className="flex flex-auto text-[#0000008a]">
                                          {/* Assigned on:
                                              {useFormattedDate(
                                                value.assigned_date
                                              )} */}
                                        </div>
                                        {/* <div
                                      className={`${
                                        value.completed
                                          ? "text-[#27A745]"
                                          : "text-[#A4A029]"
                                      }`}
                                    >
                                      {value.completed
                                        ? "Completed"
                                        : "Yet to Start"}
                                    </div> */}
                                      </div>
                                      <button
                                        onClick={() => SelectionFunction(value)}
                                        className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                          selected?.id == value.id
                                            ? "bg-[#F68D1E] text-[#EEF8FB]"
                                            : "border border-[#F68D1E] text-[#F68D1E]"
                                        }`}
                                      >
                                        {selected?.id == value.id
                                          ? "Selected"
                                          : "Select"}
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                        </>
                      ))}
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-between items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <button
                    onClick={() => {
                      localStorage.setItem("migoto-url", "/assigned-language");
                      navigate("/assigned-language", { replace: true });
                    }}
                    className="h-auto w-[10rem] xl:w-[8rem] 2xl:w-[10rem] border border-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#F68D1E] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                  >
                    <img src="./leftarrow.svg" alt="LeftArrow" loading="lazy" />
                    back
                  </button>
                  <button
                    onClick={() => NavigateFunction()}
                    className="h-auto w-[10rem] xl:w-[8rem] 2xl:w-[10rem] bg-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#FFFFFF] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                  >
                    Next{" "}
                    <img
                      src="./rightarrow.svg"
                      alt="RightArrow"
                      loading="lazy"
                    />
                  </button>
                </div>
              </div>
              <div
                className={`transition-all duration-700 ease-in-out h-full 
                  w-[20rem]
                bg-[#FFFFFF8F] inset-shadow-sm inset-shadow-[#ffffff] rounded-r-[10px] cursor-default`}
              >
                <AssignSideMenu index={8} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssignedBotVoice;
