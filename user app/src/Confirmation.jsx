import { useEffect, useRef, useState } from "react";
import AssignSideMenu from "./components/AssignSideMenu";
import HeaderMenu from "./components/HeaderMenu";
import { useNavigate } from "react-router";
import { FaPlayCircle, FaRegEdit } from "react-icons/fa";
import { HiPauseCircle } from "react-icons/hi2";
import { Visualizer } from "react-sound-visualizer";
import { useFormattedDate } from "./hooks/useFormattedDate";

const Confirmation = () => {
  let navigate = useNavigate();

  const NavigateFunction = () => {
    localStorage.setItem("migoto-url", "/conversation");
    navigate("/conversation", { replace: true });
  };

  useEffect(() => {
    FetchDatas();
  }, []);
  // Store User selected data's
  const [course, setCourse] = useState(null);
  const [reload, setReload] = useState(null);
  const [module, setModule] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [mode, setMode] = useState(null);
  const [avatar, setAvatar] = useState(null);
  const [language, setLanguage] = useState(null);
  const [voice, setVoice] = useState(null);
  const [environment, setEnvironment] = useState(null);
  // Fetch Selected datas from localstorage
  const FetchDatas = () => {
    if (localStorage.getItem("migoto-token") == null) {
      navigate("/login", { replace: true });
    }
    if (localStorage.getItem("migoto-course") != null) {
      setCourse(JSON.parse(localStorage.getItem("migoto-course")));
    }
    if (localStorage.getItem("migoto-module") != null) {
      setModule(JSON.parse(localStorage.getItem("migoto-module")));
    }
    if (localStorage.getItem("migoto-scenario") != null) {
      setScenario(JSON.parse(localStorage.getItem("migoto-scenario")));
    }
    if (localStorage.getItem("migoto-mode") != null) {
      setMode(JSON.parse(localStorage.getItem("migoto-mode")));
    }

    if (localStorage.getItem("migoto-avatar") != null) {
      setAvatar(JSON.parse(localStorage.getItem("migoto-avatar")));
    }
    if (localStorage.getItem("migoto-language") != null) {
      setLanguage(JSON.parse(localStorage.getItem("migoto-language")));
    }
    if (localStorage.getItem("migoto-voice") != null) {
      setVoice(JSON.parse(localStorage.getItem("migoto-voice")));
    }
    if (localStorage.getItem("migoto-environment") != null) {
      setEnvironment(JSON.parse(localStorage.getItem("migoto-environment")));
    }
  };

  const audioRef = useRef(new Audio());
  const [mediaStream, setMediaStream] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const generateTTS = async (props) => {
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
              {course && course?.title}
            </div>
            <div className="h-full w-full bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px] flex">
              <div className="h-full w-[80rem]">
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <div className="flex flex-auto justify-start">
                    <div>
                      <div className="flex items-center space-x-[10px]">
                        <span className="text-[16px] xl:text-[14px] 2xl:text-[16px] text-[#131F49]">
                          Confirmation
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="relative w-[247px] xl:w-[175px] 2xl:w-[247px]">
                    <input
                      type="text"
                      placeholder="Search"
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
                  <div className="h-full w-full flex flex-wrap gap-x-[5rem] xl:gap-x-[2.5rem] 2xl:gap-x-[5rem] space-y-[36px] overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                    {/*Cource Container */}
                    <div>
                      <div className="text-[#131F49] text-[16px] my-[10px]">
                        Course:
                      </div>
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[19rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-pointer">
                        <div className="h-full w-full">
                          {course?.thumbnail_url == "string" ? (
                            <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center bg-amber-50">
                              {course?.name}
                            </p>
                          ) : (
                            <img
                              loading="lazy"
                              src={course?.thumbnail_url}
                              alt={course?.name}
                              className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t-[5px]"
                            />
                          )}
                          <div className="h-[45%] w-full">
                            <div className="h-[4.8rem] xl:h-[3.5rem] 2xl:h-[4.8rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                {course?.title}
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-3">
                                {course?.description}
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                    Assigned on:{" "}
                                    {useFormattedDate(course?.assigned_date)}
                                  </div>
                                  <div className="text-[#A4A029]">
                                    <FaRegEdit
                                      size={20}
                                      onClick={() => {
                                        localStorage.removeItem(
                                          "migoto-module"
                                        );
                                        localStorage.removeItem(
                                          "migoto-scenario"
                                        );
                                        localStorage.removeItem("migoto-mode");
                                        localStorage.removeItem(
                                          "migoto-avatar"
                                        );
                                        localStorage.removeItem(
                                          "migoto-language"
                                        );
                                        localStorage.removeItem("migoto-voice");
                                        localStorage.removeItem(
                                          "migoto-environment"
                                        );
                                        navigate("/assigned-course", {
                                          replace: true,
                                        });
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {/* Module Container */}
                    <div>
                      <div className="text-[#131F49] text-[16px] my-[10px]">
                        Module:
                      </div>
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[19rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-pointer">
                        <div className="h-full w-full">
                          {module?.thumbnail_url == "string" ? (
                            <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center bg-amber-50">
                              {module?.name}
                            </p>
                          ) : (
                            <img
                              src={module?.thumbnail_url}
                              loading="lazy"
                              alt={module?.name}
                              className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t-[5px]"
                            />
                          )}
                          <div className="h-[45%] w-full">
                            <div className="h-[4.8rem]  xl:h-[3.5rem] 2xl:h-[4.8rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                {module?.title}
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-3">
                                {module?.description}
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                    {/* Assigned on: {module?.assignDate} */}
                                  </div>
                                  <div className="text-[#A4A029]">
                                    <FaRegEdit
                                      size={20}
                                      onClick={() => {
                                        localStorage.removeItem(
                                          "migoto-scenario"
                                        );
                                        localStorage.removeItem("migoto-mode");
                                        localStorage.removeItem(
                                          "migoto-avatar"
                                        );
                                        localStorage.removeItem(
                                          "migoto-language"
                                        );
                                        localStorage.removeItem("migoto-voice");
                                        localStorage.removeItem(
                                          "migoto-environment"
                                        );
                                        navigate("/assigned-module", {
                                          replace: true,
                                        });
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {/* Scenario Container */}
                    <div>
                      <div className="text-[#131F49] text-[16px] my-[10px]">
                        Scenario:
                      </div>
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[19rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-pointer">
                        <div className="h-full w-full">
                          {scenario?.thumbnail_url == "string" ? (
                            <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center bg-amber-50">
                              {scenario?.name}
                            </p>
                          ) : (
                            <img
                              src={scenario?.thumbnail_url}
                              alt={scenario?.name}
                              loading="lazy"
                              className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t-[5px]"
                            />
                          )}
                          <div className="h-[45%] w-full">
                            <div className="h-[4.8rem]  xl:h-[3.5rem] 2xl:h-[4.8rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                {scenario?.title}
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-3">
                                {scenario?.description}
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                    {/* Assigned on: {scenario?.assignDate} */}
                                  </div>
                                  <div className="text-[#A4A029]">
                                    <FaRegEdit
                                      size={20}
                                      onClick={() => {
                                        localStorage.removeItem("migoto-mode");
                                        localStorage.removeItem(
                                          "migoto-avatar"
                                        );
                                        localStorage.removeItem(
                                          "migoto-language"
                                        );
                                        localStorage.removeItem("migoto-voice");
                                        localStorage.removeItem(
                                          "migoto-environment"
                                        );
                                        navigate("/assigned-scenario", {
                                          replace: true,
                                        });
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {/* Mode Container */}
                    <div>
                      <div className="text-[#131F49] text-[16px] my-[10px]">
                        Mode:
                      </div>
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[19rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-pointer">
                        <div className="h-full w-full">
                          {mode?.thumbnail == "string" ? (
                            <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center bg-amber-50">
                              {mode?.name}
                            </p>
                          ) : (
                            <img
                              src={mode?.thumbnail}
                              alt={mode?.name}
                              loading="lazy"
                              className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t-[5px]"
                            />
                          )}
                          <div className="h-[45%] w-full">
                            <div className="h-[4.8rem]  xl:h-[3.5rem] 2xl:h-[4.8rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                {mode?.title}
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-3">
                                {mode?.description}
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                    {/* Assigned on: {mode?.assignDate} */}
                                  </div>
                                  <div className="text-[#A4A029]">
                                    <FaRegEdit
                                      size={20}
                                      onClick={() => {
                                        localStorage.removeItem(
                                          "migoto-avatar"
                                        );
                                        localStorage.removeItem(
                                          "migoto-language"
                                        );
                                        localStorage.removeItem("migoto-voice");
                                        localStorage.removeItem(
                                          "migoto-environment"
                                        );
                                        navigate("/assigned-mode", {
                                          replace: true,
                                        });
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {/* Avatar Container */}
                    <div>
                      <div className="text-[#131F49] text-[16px] my-[10px]">
                        Avatar:
                      </div>
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[19rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-pointer">
                        <div className="h-full w-full">
                          {avatar?.selected?.thumbnail_url == "string" ? (
                            <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center bg-amber-50">
                              {avatar?.selected?.name}
                            </p>
                          ) : (
                            <img
                              src={avatar?.selected?.thumbnail_url}
                              loading="lazy"
                              alt={avatar?.selected?.name}
                              className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-contain rounded-t-[5px]"
                            />
                          )}
                          <div className="h-[45%] w-full">
                            <div className="h-[4.8rem]  xl:h-[3.5rem] 2xl:h-[4.8rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                {avatar?.selected?.persona_id[0].name}
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-3">
                                Age: {avatar?.selected?.persona_id[0].age}
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-3">
                                Profession:{" "}
                                {avatar?.selected?.persona_id[0]?.persona_type}
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                    {/* Assigned on: {persona?.assignDate} */}
                                  </div>
                                  <div className="text-[#A4A029]">
                                    <FaRegEdit
                                      size={20}
                                      onClick={() => {
                                        localStorage.removeItem(
                                          "migoto-language"
                                        );
                                        localStorage.removeItem("migoto-voice");
                                        localStorage.removeItem(
                                          "migoto-environment"
                                        );
                                        navigate("/assigned-avatar", {
                                          replace: true,
                                        });
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {/* Language Container */}
                    <div>
                      <div className="text-[#131F49] text-[16px] my-[10px]">
                        Language:
                      </div>
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[19rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-pointer">
                        <div className="h-full w-full">
                          <div className="h-[4.4rem] xl:h-[9.5rem] 2xl:h-[10rem] w-full space-y-0.5 flex justify-center items-center bg-[#e9e9e952] rounded-t-[10px]">
                            <div className="place-items-center space-y-3 xl:space-y-2">
                              {language?.thumbnail_url == "string" ? (
                                <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center bg-amber-50">
                                  {language?.name}
                                </p>
                              ) : (
                                <img
                                  src={language?.thumbnail_url}
                                  loading="lazy"
                                  alt={language?.name}
                                  className="h-[8rem] xl:h-[8rem] 2xl:h-[10rem] w-full object-cover rounded-t-[5px]"
                                />
                              )}
                            </div>
                          </div>
                          <div className="h-[45%] w-full">
                            <div className="h-[4.8rem]  xl:h-[2rem] 2xl:h-[4.8rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                {language?.name}
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-3">
                                {/* {language?.description} */}
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[2.5rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                    {/* Assigned on: {language?.assignDate} */}
                                  </div>
                                  <div className="text-[#A4A029]">
                                    <FaRegEdit
                                      size={20}
                                      onClick={() => {
                                        localStorage.removeItem("migoto-voice");
                                        localStorage.removeItem(
                                          "migoto-environment"
                                        );
                                        navigate("/assigned-language", {
                                          replace: true,
                                        });
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {/* Bot voice Container */}
                    <div>
                      <div className="text-[#131F49] text-[16px] my-[10px]">
                        Voice:
                      </div>
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[19rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-pointer">
                        <div className="h-full w-full">
                          <div className="h-[55%] xl:h-[60%] 2xl:h-[60%] w-full bg-[#e9e9e954] flex justify-center items-center">
                            <div className="space-y-3.5">
                              <div
                                className="flex justify-center"
                                onClick={() => {
                                  if (!isPlaying) {
                                    audioRef.current.pause();
                                    generateTTS(voice);
                                  } else {
                                    audioRef.current.pause();
                                    setIsPlaying(false);
                                    setMediaStream(null);
                                  }
                                }}
                              >
                                {isPlaying ? (
                                  <>
                                    {isPlaying ? (
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
                              </div>
                            </div>
                          </div>
                          <div className="h-[45%] w-full">
                            <div className="h-[4.8rem] xl:h-[2.1rem] 2xl:h-[3.8rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                {voice?.name}
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                    {/* Assigned on: {voice?.assignDate} */}
                                  </div>
                                  <div className="text-[#A4A029]">
                                    <FaRegEdit
                                      size={20}
                                      onClick={() => {
                                        localStorage.removeItem(
                                          "migoto-environment"
                                        );
                                        navigate("/assigned-botvoice", {
                                          replace: true,
                                        });
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {/* Environment Container */}
                    <div>
                      <div className="text-[#131F49] text-[16px] my-[10px]">
                        Environment:
                      </div>
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[19rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-pointer">
                        <div className="h-full w-full">
                          {environment?.thumbnail_url == "string" ? (
                            <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center bg-amber-50">
                              {environment?.name}
                            </p>
                          ) : (
                            <img
                              src={environment?.thumbnail_url}
                              loading="lazy"
                              alt={environment?.name}
                              className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t-[5px]"
                            />
                          )}
                          <div className="h-[45%] w-full">
                            <div className="h-[4.8rem]  xl:h-[3.6rem] 2xl:h-[4.8rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                {environment?.name}
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-3">
                                {/* {environment?.description} */}
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                    {/* Assigned on: {environment?.assignDate} */}
                                  </div>
                                  <div className="text-[#A4A029]">
                                    <FaRegEdit
                                      size={20}
                                      onClick={() =>
                                        navigate("/assigned-environment", {
                                          replace: true,
                                        })
                                      }
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-between items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <button
                    onClick={() => {
                      localStorage.setItem(
                        "migoto-url",
                        "/assigned-environment"
                      );
                      navigate("/assigned-environment", { replace: true });
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
                <AssignSideMenu index={10} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Confirmation;
