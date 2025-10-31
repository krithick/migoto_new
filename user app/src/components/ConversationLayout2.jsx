import React, { useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import {
  IoPlaySkipForwardCircleOutline,
  IoVideocamOffOutline,
  IoVideocamOutline,
} from "react-icons/io5";
import EvaluationConversation from "./EvaluationConversation";
import TryConversation from "./TryConversation";
import { Visualizer } from "react-sound-visualizer";
import { Canvas } from "@react-three/fiber";
import LightHelper from "./LightHelper";
import ModelAnimationLoader from "./ModelAnimationLoader";
import Webcam from "react-webcam";

const ConversationLayout2 = ({
  isThinking,
  avatar,
  environment,
  avatarAction,
  audioReload,
  recording,
  mode,
  finalConversationHistory,
  language,
  setMic,
  mic,
  voice,
  setRecording,
  startRecording,
  audioStream,
  stopRecording,
  userInput,
  setUserInput,
  sendMessage,
  finishButton,
  close,
  SkipTTS,
  setCoachMessage,
  audioRef,
}) => {
  // const animationGLB = "/Character/Moh_Armature.glb";
  // const animationGLB = "/Character/Ama_Armature.glb";
  // const animationGLB = "/Character/Da_Armature.glb";
  // const animationGLB = "/Character/Joh_Armature.glb";

  // "/Character/Moh_Glass_Gls1.glb",
  // const glbfiles = [
  //   "/Character/Moh_Beard_Br1.glb",
  //   "/Character/Moh_Body_B1.glb",
  //   "/Character/Moh_Pant_Pt1.glb",
  //   "/Character/Moh_Shirt_St1.glb",
  //   "/Character/Moh_Hair_Hr1.glb",
  // ];

  // "/Character/Ama_Beard_Br1.glb",
  // const glbfiles = [
  //   "/Character/Ama_Body_B1.glb",
  //   "/Character/Ama_Pant_Pt1.glb",
  //   "/Character/Ama_Shirt_St1.glb",
  //   "/Character/Ama_Hair_Hr1.glb",
  // ];

  // "/Character/Da_Beard_Br1.glb",
  // const glbfiles = [
  //   "/Character/Da_Body_B1.glb",
  //   "/Character/Da_Pant_Pt1.glb",
  //   "/Character/Da_Shirt_St1.glb",
  //   "/Character/Da_Hair_Hr1.glb",
  // ];

  // const glbfiles = [
  //   "/Character/Joh_Beard_Br1.glb",
  //   "/Character/Joh_Body_B1.glb",
  //   "/Character/Joh_Pant_Pt1.glb",
  //   "/Character/Joh_Shirt_St1.glb",
  //   "/Character/Joh_Hair_Hr1.glb",
  // ];

  const webcamRef = useRef(null);
  const [cameraToggle, setCameraToggle] = useState(false);
  useEffect(() => {
    setTimeout(() => {
      let stream = webcamRef.current;
      if (stream?.state.hasUserMedia == false) {
        setCameraToggle(true);
        toast.error("Web camera is not available..");
      }
    }, 1000);
  }, []);

  const cameraToggleFunction = () => {
    if (!cameraToggle) {
      setCameraToggle(true);
      let stream = webcamRef.current.stream;
      const tracks = stream.getTracks();
      tracks.forEach((track) => track.stop());
    } else {
      setCameraToggle(false);
      webcamRef.current = null;
    }
  };

  const handleTextArea = (e) => {
    // Return if user presses the enter key
    if (e.nativeEvent.inputType === "insertLineBreak") {
      e.preventDefault();
      if (userInput.trim() != "") {
        sendMessage(userInput);
        setMic(true);
        setUserInput("");
      } else {
        if (!mic && !finishButton && recording) stopRecording();
        else if (finishButton) toast.error("Conversation has ended");
        else toast.error("No Input");
      }
      return;
    }

    setUserInput(e.target.value);
  };

  return (
    <div className="h-[40.8rem] xl:h-[24rem] 2xl:h-[39rem] w-full px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem] py-[15px] xl:py-[px] 2xl:py-[15px]">
      <div className="h-full w-full grid grid-cols-3 place-content-center gap-x-[5rem] xl:gap-x-0 2xl:gap-x-[1rem] overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
        {/* Conversation */}
        <div className="col-span-1 h-full w-full place-items-center">
          <div
            className={`h-[35rem] xl:h-[22rem] 2xl:h-[35rem]  bg-[#FFFFFF8F] rounded-[10px] transition-all duration-1000 ease-in-out animate-fade-left animate-ease-linear ${
              close
                ? "w-[25rem] xl:w-[19rem] 2xl:w-[25rem]"
                : "w-[25rem] xl:w-[14.5rem] 2xl:w-[21rem]"
            }`}
          >
            <div className="h-[3rem] xl:h-[2.5rem] 2xl:h-[3rem] w-full flex justify-start items-center bg-[#131F49] text-[#FFFFFF] text-[16px] xl:text-[14px] 2xl:text-[16px] rounded-t-[10px] px-5">
              {avatar?.selected?.persona_id[0]?.name}
            </div>
            <div className="h-[28rem] xl:h-[19.5rem] 2xl:h-[32rem] w-full relative">
              <div className="absolute inset-0 h-full w-full">
                <img
                  src={`./Environment/Potrait_${environment?.name}.png`}
                  // src={`/Environment/Potrait_Environment_2.png`}
                  alt="environment"
                  className="h-full w-full object-cover rounded-b-[5px]"
                  loading="lazy"
                />
              </div>
              <Canvas
                orthographic
                className="h-full w-full rounded-b-[5px]"
                camera={{
                  zoom: 16,
                  far: 2000,
                  position: [0, 11.5, 10],
                  rotation: [-0, 0, 0],
                }}
              >
                <LightHelper />
                <ModelAnimationLoader
                  recording={recording}
                  avatarAction={avatarAction}
                  audioReload={audioReload}
                  // animationGLB={animationGLB}
                  // glbfiles={glbfiles}
                  animationGLB={avatar?.selected.animation}
                  glbfiles={avatar?.selected.glb}
                />
              </Canvas>
            </div>
          </div>
        </div>
        <div className="col-span-1 h-full w-full place-items-center">
          <div
            className={`h-[35rem] xl:h-[22rem] 2xl:h-[35rem]  bg-[#FFFFFF8F] rounded-[10px] transition-all duration-1000 ease-in-out animate-fade-left animate-ease-linear ${
              close
                ? "w-[25rem] xl:w-[17rem] 2xl:w-[25rem]"
                : "w-[25rem] xl:w-[14.5rem] 2xl:w-[21rem]"
            }`}
          >
            <div className="h-[3rem] xl:h-[2.5rem] 2xl:h-[3rem] w-full flex justify-start items-center bg-[#131F49] text-[#FFFFFF] text-[16px] xl:text-[14px] rounded-t-[10px] px-5">
              <div className="flex flex-auto">User</div>
              <div className="flex text-white">
                <label className="relative inline-flex cursor-pointer items-center">
                  <input
                    onChange={() => cameraToggleFunction()}
                    type="checkbox"
                    value=""
                    checked={cameraToggle ? true : false}
                    className="peer sr-only"
                  />
                  <div className="peer flex h-8 xl:h-6 2xl:h-8 items-center gap-4 rounded-full bg-orange-600 px-2 xl:px-0.5 2xl:px-2 after:absolute after:left-1 xl:after:left-0.5 2xl:after:left-2 after:h-6 after:w-10 xl:after:w-10 2xl:after:w-10 after:rounded-full after:bg-white/40 after:transition-all after:content-[' '] peer-checked:bg-stone-600 peer-checked:after:translate-x-full peer-focus:outline-none  text-sm text-center text-white">
                    <span className="ml-2">
                      {cameraToggle ? "Off" : <IoVideocamOutline size={20} />}
                    </span>
                    <span className="mx-2">
                      {!cameraToggle ? (
                        "ON"
                      ) : (
                        <IoVideocamOffOutline size={20} />
                      )}
                    </span>
                  </div>
                </label>
              </div>
            </div>
            <div className="h-[28rem] xl:h-[19.5rem] 2xl:h-[32rem] rounded-b-[5px] w-full relative">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                mirrored={true}
                className={`transition-all duration-700 ease-in-out h-full w-full object-cover ${
                  !cameraToggle ? "block" : "hidden"
                }`}
              />
            </div>
          </div>
        </div>
        <div className="col-span-1 h-full w-full place-items-center">
          <div
            className={`h-[35rem] xl:h-[22rem] 2xl:h-[35rem]  bg-[#FFFFFF8F] rounded-[10px] transition-all duration-1000 ease-in-out animate-fade-left animate-ease-linear ${
              close
                ? "w-[25rem] xl:w-[19rem] 2xl:w-[25rem]"
                : "w-[25rem] xl:w-[16.5rem] 2xl:w-[21rem]"
            }`}
          >
            <div className="h-[3rem] xl:h-[2.5rem] 2xl:h-[3rem] w-full flex justify-start items-center bg-[#131F49] text-[#FFFFFF] text-[16px] xl:text-[14px] rounded-t-[10px] px-5">
              Conversation
            </div>
            <div className="h-[28rem] xl:h-[15.5rem] 2xl:h-[28rem] w-full flex justify-center items-center pr-2 py-1.5">
              {/* Conversation Dialog */}
              {mode?.title == "Try Mode" ? (
                <TryConversation
                  isThinking={isThinking}
                  conversation={finalConversationHistory}
                  language={language}
                  mic={mic}
                  voice={voice}
                  avatar={avatar?.selected}
                  finish={finishButton}
                  setCoachMessage={setCoachMessage}
                  audioRef={audioRef}
                />
              ) : (
                <EvaluationConversation
                  isThinking={isThinking}
                  conversation={finalConversationHistory}
                  avatar={avatar?.selected}
                  finish={finishButton}
                  language={language?.title}
                  audioRef={audioRef}
                  mic={mic}
                />
              )}
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (userInput.trim() != "") {
                  sendMessage(userInput);
                  setMic(true);
                  setUserInput("");
                } else {
                  if (!mic && !finishButton && recording) stopRecording();
                  else if (finishButton) toast.error("Conversation has ended");
                  else if (userInput.trim() === "") toast.error("No Input");
                }
              }}
              className="h-[4rem] w-full bg-[#131f4998] rounded-b-[10px] flex justify-between items-center px-3.5 xl:px-1  py-1"
            >
              <div className="text-center -space-y-1.5">
                <div
                  className={`h-8 w-8 flex justify-center items-center rounded-full ${
                    !mic && !finishButton
                      ? "bg-[#131F49] text-white cursor-pointer"
                      : "bg-[#9599a7b0]"
                  }`}
                  onClick={() => {
                    if (recording && !finishButton) {
                      setRecording(false);
                    } else if (finishButton) {
                      toast.error("Conversation has ended.");
                    } else if (!mic) {
                      setUserInput("");
                      startRecording();
                    }
                  }}
                >
                  <img
                    loading="lazy"
                    src={recording ? "./close_white.svg" : "./speak.svg"}
                    alt="speak"
                    className={`h-full w-full ${recording ? "p-2" : "p-1"}`}
                  />
                </div>
                <span className="text-[#FFFFFF] text-[8px]">
                  {recording ? "Stop" : "Speak"}
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
                  <textarea
                    disabled={mic || finishButton}
                    type="text"
                    value={userInput}
                    onChange={(e) => handleTextArea(e)}
                    placeholder="Type Here"
                    className="w-60 xl:w-36 2xl:w-60 h-10 py-0.5 px-1.5 bg-[#C7DFF09C] flex items-center rounded-[5px] text-[12px] font-600 focus:outline-none text-[#131F49] resize-none line-clamp-2 wrap-break-word overflow-hidden"
                  />
                )}
              </div>
              {!mic ? (
                <div className="text-center -space-y-1.5">
                  {/* Send Button */}
                  <button
                    type="submit"
                    className={`h-8 w-8 flex justify-center items-center rounded-full ${
                      !mic && !finishButton
                        ? "bg-[#FFFFFF] text-[#F68D1E] cursor-pointer"
                        : "bg-[#9599a7b0]"
                    }`}
                  >
                    <img
                      src="./send.svg"
                      loading="lazy"
                      alt="Send"
                      className="h-full w-full p-2"
                    />
                  </button>
                  <span className="text-[#FFFFFF] text-[8px]">Send</span>
                </div>
              ) : (
                <div className="text-center -space-y-1.5">
                  {/* Skip Button */}
                  <div
                    onClick={SkipTTS}
                    className={`h-8 w-8 flex justify-center items-center rounded-full bg-[#FFFFFF] text-[#F68D1E] cursor-pointer`}
                  >
                    <IoPlaySkipForwardCircleOutline className="h-full w-full p-2" />
                  </div>
                  <span className="text-[#FFFFFF] text-[8px]">Skip</span>
                </div>
              )}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationLayout2;
