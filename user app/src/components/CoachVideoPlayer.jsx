import { IoClose } from "react-icons/io5";
import { useEffect, useRef, useState } from "react";
import { FaPause } from "react-icons/fa";
import { MdOutlinePlayCircle } from "react-icons/md";
import axios from "axios";
import toast from "react-hot-toast";
import instance from "../service";

const CoachVideoPlayer = ({ message, setCoachMessage, setMic, avatar }) => {
  const [showButton, setShowButton] = useState(false);
  const vidRef = useRef(null);
  const audioRef = useRef(new Audio());
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(false);
  const [showControls, setShowControls] = useState(false);
  const [ttsAPICall, setTtsAPICall] = useState(false);
  const [audioURL, setAudioURL] = useState(null);

  const handlePlayPause = () => {
    if (isPlaying) {
      vidRef.current.pause();
      audioRef.current.pause();
    } else {
      vidRef.current.play();
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    const video = vidRef.current;
    const currentTime = video.currentTime;
    // console.log("currentTime",currentTime);
    const duration = video.duration;
    // console.log("DurationTime",duration);
    setProgress((currentTime / duration) * 100);
  };

  const handleFinished = () => {
    vidRef.current.pause();
    setIsPlaying(false);
  };

  useEffect(() => {
    Request_to_WitAI_for_TTS();
    // onOpen();
    const video = vidRef.current;
    if (video) {
      video.addEventListener("timeupdate", handleTimeUpdate);
      video.addEventListener("ended", handleFinished);
    }
  }, []);

  // Function to handle text-to-speech request
  const Request_to_WitAI_for_TTS = async () => {
    if (!ttsAPICall) {
      setTtsAPICall(true);

      const getOppositeGenderVoice = () => {
        const migotoVoice = localStorage.getItem("migoto-voice")
          ? JSON.parse(localStorage.getItem("migoto-voice"))
          : null;

        if (migotoVoice) {
          const { language_code } = migotoVoice;
          console.log("language_code", language_code);

          const isMale =
            avatar?.selected?.gender === "male" || avatar?.gender === "male";

          console.log("isMale", isMale);
          const voiceMap = {
            "en-IN": isMale ? "en-IN-AashiNeural" : "en-IN-AaravNeural",
            "hi-IN": isMale ? "hi-IN-AartiNeural" : "hi-IN-ArjunNeural",
            "ta-IN": isMale ? "ta-IN-PallaviNeural" : "ta-IN-ValluvarNeural",
            "en-US": isMale ? "en-IN-AashiNeural" : "en-IN-AaravNeural",
          };
          console.log("language_code", voiceMap[language_code]);
          return voiceMap[language_code] || "en-IN-AaravNeural";
        }

        return avatar?.selected?.gender === "male" || avatar?.gender === "male"
          ? "en-IN-AashiNeural"
          : "en-IN-AaravNeural";
      };

      const formData = new FormData();
      formData.append("message", message.replace(/[\*\#]|\[CORRECT\]/g, ""));
      formData.append("voice_id", getOppositeGenderVoice());
      // formData.append(
      //   "voice_id",
      //   `${
      //     avatar?.gender == "male" ? "en-IN-AashiNeural" : "en-IN-AaravNeural"
      //   }`
      // );
      try {
        const response = await instance.post("/speech/tts", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
          },
          responseType: "arraybuffer",
        });

        const audioBlob = new Blob([response.data], { type: "audio/wav" });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioURL(audioUrl);
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        setShowButton(true);

        audioRef.current.onplay = () => {
          vidRef.current.pause();
          handlePlayPause();
        };
        audioRef.current.onended = () => {
          vidRef.current.pause();
          vidRef.current.currentTime = 0;
          setIsPlaying(false);
          setProgress(true);
          audioRef.current = new Audio();
        };
      } catch (err) {
        console.error("TTS error:", err);
      }
    } else {
      console.log("restart conversation");

      try {
        // const response = await instance.post("/speech/tts", formData, {
        //   headers: {
        //     "Content-Type": "multipart/form-data",
        //     Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
        //   },
        //   responseType: "arraybuffer",
        // });

        // const audioBlob = new Blob([response.data], { type: "audio/wav" });
        // const audioUrl = URL.createObjectURL(audioBlob);

        audioRef.current.src = audioURL;
        audioRef.current.play();
        setShowButton(true);

        audioRef.current.onplay = () => {
          vidRef.current.pause();
          handlePlayPause();
        };
        audioRef.current.onended = () => {
          vidRef.current.pause();
          vidRef.current.currentTime = 0;
          setIsPlaying(false);
          setProgress(true);
          audioRef.current = new Audio();
          // setShowButton(false);
        };
      } catch (err) {
        console.error("TTS error:", err);
      }
    }
  };

  return (
    <>
      {/* <div className="flex justify-center ">
        <div className="bg-[#C6C6C66E] p-3 rounded-[10px] space-y-1.5">
          <div className="flex">
            <img
              src="./user_conversation.svg"
              alt="user_conversation"
              className="w-8 h-8 xl:w-6 xl:h-6 2xl:w-8 2xl:h-8 object-contain bg-[#131F49] p-1.5 rounded-full"
            />
            <div className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] ml-2 py-1 px-4 bg-[#ffffff9d] rounded text-[12px] border border-[#131f497c]">
              <div className="text-[12px] font-medium">Coach</div>
              <div className="text-[10px] font-normal">
                {message.replace(/[\*\#]|\[CORRECT\]/g, "")}
              </div>
            </div>
          </div>
          <button
            onClick={() => {
              setPopUp(true);
              setCoachMessage(message.replace(/[\*\#]|\[CORRECT\]/g, ""));
            }}
            className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] ml-10 xl:ml-8 2xl:ml-10 py-1.5 px-4 bg-[#EFF7FC] rounded text-[12px] border border-[#131f497c] cursor-pointer"
          >
            Replay
          </button>
        </div>
      </div> */}

      {/* {popup && ( */}
      <div className="absolute inset-0 h-[35.5rem] xl:h-[35.5rem] 2xl:h-[56.5rem]  w-screen mt-[58px] xl:mt-[44px] 2xl:mt-[58px]  z-20 flex justify-center items-center bg-[#000000ce] backdrop-blur">
        <div className="h-[28rem] w-[40rem] bg-[#FFFFFF] inset-shadow-[6px] rounded-[10px]">
          <div className="h-full w-auto rounded">
            <div className="h-[2.5rem] w-full flex justify-center items-center gap-2 px-5 py-2">
              <div className="h-full w-auto flex flex-auto items-center font-bold text-[#131F49] text-[18px]">
                Coach
              </div>
              <div
                className="h-full w-auto flex justify-center items-center font-bold rounded-full text-[18px] px-1 py-1 bg-[#131F49] text-white cursor-pointer"
                onClick={() => {
                  if (!isPlaying) {
                    if (audioRef.current) {
                      audioRef.current.pause();
                      audioRef.current.currentTime = 0; // Reset to the beginning
                      console.log("Audio stopped");
                    }
                    setIsPlaying(false);
                    setMic(false);
                    // setPopUp(false);
                    setCoachMessage(null);
                  } else {
                    toast("Kindly listen to the coach first", {
                      icon: "👏",
                    });
                  }
                }}
              >
                <IoClose />
              </div>
            </div>
            <div className="h-[25rem] w-full flex flex-col space-y-5">
              <div className="h-full w-full flex flex-col">
                <div
                  className="relative h-full w-full px-3"
                  onMouseEnter={() => setShowControls(true)}
                  onMouseLeave={() => setShowControls(false)}
                >
                  <video
                    ref={vidRef}
                    // autoPlay
                    loop
                    className="w-full h-full rounded-lg"
                    controls={false}
                    // onClick={Request_to_WitAI_for_TTS}
                  >
                    <source
                      src={`./videos/${
                        avatar?.selected?.gender === "male"
                          ? "female_coach"
                          : "male_coach"
                      }.mp4`}
                      type="video/mp4"
                    />
                  </video>
                  {showControls && (
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 px-2 py-2 text-white rounded-full flex flex-col items-center">
                      {showButton && (
                        <button
                          onClick={() => {
                            Request_to_WitAI_for_TTS();
                          }}
                          className="bg-[#131F49] text-white px-2 py-2 rounded-full shadow-md"
                        >
                          {isPlaying ? (
                            <FaPause className="text-[15px] m-2" />
                          ) : (
                            <MdOutlinePlayCircle className="text-[30px]" />
                          )}
                        </button>
                      )}
                      {/* <span>{isPlaying ? "Pause" : "Play"}</span> */}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* )} */}
    </>
  );
};

export default CoachVideoPlayer;
