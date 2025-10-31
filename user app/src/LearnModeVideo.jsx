import HeaderMenu from "./components/HeaderMenu";
import AssignSideMenu from "./components/AssignSideMenu";
import FinishConversationButtons from "./components/FinishConversationButtons";
import { useNavigate } from "react-router";
import { useEffect, useRef, useState } from "react";
import { GiSpeaker } from "react-icons/gi";
import { FaPause } from "react-icons/fa";
import { MdOutlinePlayCircle } from "react-icons/md";
import instance from "./service";

const LearnModeVideo = () => {
  let navigate = useNavigate();
  const vidRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [volume, setVolume] = useState(1);
  const [videoDetails, setVideoDetails] = useState(0);
  const [selectedVideo, setSelectedVideo] = useState(null);

  const handlePlayPause = () => {
    if (isPlaying) {
      vidRef.current.pause();
    } else {
      vidRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    const video = vidRef.current;
    const currentTime = video.currentTime;
    const duration = video.duration;
    setProgress((currentTime / duration) * 100);
  };

  const handleSkipVideo = (field, value) => {
    const video = vidRef.current;
    const duration = video.duration;
    let newTime = video.currentTime;

    if (field === "prev") {
      newTime = Math.max(newTime - value, 0);
    }
    if (field === "next") {
      newTime = Math.min(newTime + value, duration);
    }
    video.currentTime = newTime;
    setProgress((newTime / duration) * 100);
  };

  const handleFinished = () => {
    vidRef.current.pause();
    setIsPlaying(false);
  };

  const handleFullscreen = () => {
    const videoContainer = vidRef.current;
    if (videoContainer) {
      videoContainer.requestFullscreen();
    }
  };

  const volumeFunction = (e) => {
    const newVolume = e.target.value / 100;
    setVolume(newVolume);
    const video = vidRef.current;
    video.volume = newVolume;
  };

  useEffect(() => {
    const video = vidRef.current;
    if (video) {
      video.addEventListener("timeupdate", handleTimeUpdate);
      video.addEventListener("ended", handleFinished);
    }
  }, [selectedVideo]);

  useEffect(() => {
    fetchAssignedLearnModeVideoDetails();
  }, []);

  // fetch assigned avatar details
  const fetchAssignedLearnModeVideoDetails = async () => {
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
          `/avatar-interactions/${avatarIntraction?.avatar_interaction}?expand=assigned_videos`,
          {
            headers,
          }
        )
        .then((response) => {
          setVideoDetails(response.data.assigned_videos);
          setSelectedVideo(response.data.assigned_videos[0]);
        })
        .catch((error) => {
          console.error("Error fetching assigned modules:", error);
        });
    } catch (error) {
      console.error("Error fetching assigned modules:", error);
    }
  };
  return (
    <div className="absolute inset-0 backdrop-blur-[68px]">
      <div className="h-screen w-screen relative">
        <HeaderMenu />
        <div className="h-[35.5rem] xl:h-[38rem] 2xl:h-[56rem] w-screen flex items-center">
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
                        onClick={() =>
                          navigate("/learn-mode-bot", { replace: true })
                        }
                        className={`bg-[#131f490f] w-[12rem] xl:w-[11rem] h-[2rem] 2xl:h-[2.5rem] px-4 py-1  text-[#535BA4] border-b-2  text-[12px]  rounded items-center justify-center flex gap-x-3 cursor-pointer`}
                      >
                        <img
                          loading="lazy"
                          src={`./LearnBotConversation.svg`}
                          alt="BotConversation"
                        />
                        Bot Conversation
                      </button>
                      <button
                        className={`bg-[#131f490f] w-[12rem] xl:w-[11rem] h-[2rem] 2xl:h-[2.5rem] px-4 py-1 border-b-4 border-b-[#E98A3C] text-[#E98A3C] text-[12px]  rounded items-center justify-center flex gap-x-3 cursor-pointer`}
                      >
                        <img
                          src={`./LearnVideo_select.svg`}
                          alt="LearnVideo"
                          loading="lazy"
                        />
                        Video
                      </button>
                      <button
                        onClick={() =>
                          navigate("/learn-mode-pdf", { replace: true })
                        }
                        className={`bg-[#131f490f] w-[12rem] xl:w-[11rem] h-[2rem] 2xl:h-[2.5rem] px-4 py-1  text-[#535BA4] border-b-2  text-[12px] rounded items-center justify-center flex gap-x-3 cursor-pointer`}
                      >
                        <img
                          src={`./LearnPDF.svg`}
                          alt="LearnVideo"
                          loading="lazy"
                        />
                        Document
                      </button>
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[40.8rem] xl:h-[25.5rem] 2xl:h-[40.8rem] w-full px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem] py-[15px] xl:py-[10px] 2xl:py-[25px]">
                  <div className="h-full w-full flex justify-center gap-x-[5rem] xl:gap-x-[1rem] 2xl:gap-x-[3rem]">
                    <div className="h-[35rem] xl:h-[24rem] 2xl:h-[37.5rem] w-[25rem] xl:w-[14rem] 2xl:w-[20rem] bg-[#FFFFFF8F] rounded-[10px]">
                      <div className="h-[3rem] w-full flex items-center px-3 text-[#FFFFFF] text-[14px] rounded-t-[10px] bg-[#131F49]">
                        Document
                      </div>
                      <div className="h-[34rem] xl:h-[21rem] 2xl:h-[34rem] w-full pr-2 py-2 space-y-3 ">
                        <div className="h-full w-full px-2 space-y-2 overflow-y-auto [&::-webkit-scrollbar]:w-[3px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                          {videoDetails &&
                            videoDetails.map((value, index) => (
                              <div
                                key={index}
                                className="[6rem] w-full p-2 space-x-2 flex items-center rounded-[10px] bg-[#FFFFFF] border border-[#7070706E]"
                              >
                                <img
                                  loading="lazy"
                                  src={
                                    selectedVideo?.id == value.id
                                      ? "./LearnVideo_select.svg"
                                      : "./LearnVideo.svg"
                                  }
                                  // src={"/LearnVideo.svg"}
                                  // src={value.thumbnail_url}
                                  alt={value.title}
                                  className="h-[3rem] w-auto object-contain"
                                />
                                <div className="space-y-1.5 w-full">
                                  <p className="text-[#131F49] text-[12px] xl:text-[10px] font-medium">
                                    {value.title}
                                  </p>
                                  <p className="text-[#707070] text-[10px] xl:text-[8px] font-normal line-clamp-2">
                                    {value.description}
                                  </p>
                                  <div
                                    onClick={() => setSelectedVideo(value)}
                                    className="flex justify-end text-[#F68D1E] text-[12px] xl:text-[10px] underline cursor-pointer"
                                  >
                                    {selectedVideo?.id == value.id
                                      ? "Opened"
                                      : "Open"}
                                  </div>
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                    <div className="h-[35rem] xl:h-[21rem] 2xl:h-[32rem] w-[25rem] xl:w-[40rem] 2xl:w-[55rem] bg-[#FFFFFF8F] rounded-lg">
                      <div className="h-[3rem] w-full flex items-center px-3 text-[#FFFFFF] text-[14px] rounded-t-[10px] bg-[#131F49]">
                        Video Title
                      </div>
                      <div className="flex justify-center items-start h-full w-full">
                        {selectedVideo && (
                          <div className="xl:h-[15rem] 2xl:h-[26rem] w-full relative rounded-lg">
                            <video
                              ref={vidRef}
                              className="h-full w-full rounded-t-lg object-contain"
                              controls={false}
                            >
                              <source
                                // src=".https://meta.novactech.in:7445/uploads/video/20250508064448_04f87011.mp4"
                                src={selectedVideo.url}
                                type="video/mp4"
                              />
                            </video>
                            <div className="absolute inset-x-0 h-[3rem] w-full px-3 py-2 bg-[#131F4933] rounded-b-lg">
                              <div className="h-full w-full flex flex-col justify-center items-end">
                                {/* Progress Bar */}
                                <div className=" flex justify-start items-center w-full bg-opacity-75 rounded-full p-1">
                                  <div
                                    className="bg-[#131F49] rounded-full transition-all w-full h-1"
                                    style={{ width: `${progress}%` }}
                                  ></div>
                                </div>
                                <div className="flex justify-between items-center h-full w-full space-x-[200px] xl:space-x-[100px]">
                                  {/* Volume Control */}
                                  <div>
                                    <div className="flex items-center w-32 xl:w-20">
                                      <GiSpeaker className="text-[30px] text-[#131F49]" />
                                      <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        value={volume * 100}
                                        onChange={volumeFunction}
                                        className="w-full accent-[#131F49] h-1.5"
                                      />
                                    </div>
                                  </div>

                                  <div className="flex justify-evenly items-center space-x-3 h-full w-auto pr-10">
                                    {/* Prev Buttons */}
                                    <button
                                      onClick={() =>
                                        handleSkipVideo("prev", 10)
                                      }
                                      className="text-white px-2 py-2 xl:px-1.5 xl:py-0.5 rounded bg-[#131F49] bg-opacity-85"
                                    >
                                      <img
                                        loading="lazy"
                                        src="./pre10.svg"
                                        alt="fullscreen"
                                        className=""
                                      />
                                    </button>
                                    {/* Play Button (hidden by default, appears on hover) */}
                                    <button
                                      onClick={handlePlayPause}
                                      className="bg-[#131F49] bg-opacity-85 text-white px-2 py-2 xl:px-1.5 xl:py-0.5 rounded"
                                    >
                                      {isPlaying ? (
                                        <FaPause className="text-[17px]" />
                                      ) : (
                                        <MdOutlinePlayCircle className="text-[17px]" />
                                      )}
                                    </button>
                                    {/*  Next Buttons */}
                                    <button
                                      onClick={() =>
                                        handleSkipVideo("next", 10)
                                      }
                                      className="text-white px-2 py-2 xl:px-1.5 xl:py-0.5 rounded bg-[#131F49] bg-opacity-85"
                                    >
                                      <img
                                        loading="lazy"
                                        src="./next10.svg"
                                        alt="fullscreen"
                                        className=""
                                      />
                                    </button>
                                  </div>
                                  {/* Fullscreen Button */}
                                  <div>
                                    <button
                                      onClick={handleFullscreen}
                                      className="text-white px-2 py-2 xl:px-1.5 xl:py-0.5 rounded bg-[#131F49] bg-opacity-85"
                                    >
                                      <img
                                        loading="lazy"
                                        src="./fullscreen.svg"
                                        alt="fullscreen"
                                      />
                                    </button>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-between items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <button
                    onClick={() => navigate("/confirmation", { replace: true })}
                    className="h-auto w-[10rem] xl:w-[12rem] 2xl:w-[13rem] border border-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#F68D1E] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                  >
                    <img src="./leftarrow.svg" alt="LeftArrow" loading="lazy" />
                    back
                  </button>
                  <FinishConversationButtons mode={"learn"} />
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

export default LearnModeVideo;
