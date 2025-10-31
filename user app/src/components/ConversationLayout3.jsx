import { Canvas } from "@react-three/fiber";
import React from "react";
import toast from "react-hot-toast";
import LightHelper from "./LightHelper";
import ModelAnimationLoader from "./ModelAnimationLoader";
import EvaluationConversation from "./EvaluationConversation";
import TryConversation from "./TryConversation";
import { Visualizer } from "react-sound-visualizer";
import { IoPlaySkipForwardCircleOutline } from "react-icons/io5";

const ConversationLayout3 = ({
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
  SkipTTS,
  setCoachMessage,
  audioRef,
}) => {
  const animationGLB = "/Character/Moh_Armature.glb";

  // "/Character/Moh_Glass_Gls1.glb",
  const glbfiles = [
    "/Character/Moh_Beard_Br1.glb",
    "/Character/Moh_Body_B1.glb",
    "/Character/Moh_Hair_Hr1.glb",
    "/Character/Moh_Pant_Pt1.glb",
    "/Character/Moh_Shirt_St1.glb",
  ];

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
      <div className="h-full w-full flex justify-center items-center gap-x-[5rem] xl:gap-x-[2.5rem] 2xl:gap-x-[5rem] overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
        {/* Conversation */}
        <div className="h-[28rem] xl:h-[22rem] 2xl:h-[37rem] w-full relative">
          <div className="absolute inset-0 h-full w-full">
            <img
              src={`./Environment/${environment?.name}.png`}
              loading="lazy"
              // src={`/Environment/Environment_2.png`}
              alt="background"
              className="h-full w-full object-cover rounded-[5px]"
            />
          </div>
          <Canvas
            orthographic
            className="h-full w-full"
            camera={{
              zoom: 20,
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
          <div className="absolute inset-y-0 right-0 px-3 place-content-center">
            <div className="h-[35rem] xl:h-[21.5rem] 2xl:h-[35rem] w-[25rem] xl:w-[15rem] 2xl:w-[22rem] rounded-[10px] bg-[#FFFFFF8F]">
              <div className="h-[3rem] xl:h-[2.5rem] 2xl:h-[3rem] w-full flex justify-start items-center bg-[#131F49] text-[#FFFFFF] text-[16px] xl:text-[14px] rounded-t-[10px] px-5">
                Conversation
              </div>
              <div className="h-[28rem] xl:h-[15rem] 2xl:h-[28rem] w-full flex justify-center items-center pr-2 py-1.5">
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
              {/* Input Bar */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (userInput.trim() != "") {
                    sendMessage(userInput);
                    setMic(true);
                    setUserInput("");
                  } else {
                    if (!mic && !finishButton && recording) stopRecording();
                    else if (finishButton)
                      toast.error("Conversation has ended");
                    else if (userInput.trim() === "") toast.error("No Input");
                  }
                }}
                className="h-[4rem] w-full bg-[#131f4998] rounded-b-[10px] flex justify-between items-center px-3.5 xl:px-1  py-1"
              >
                {/* Mic Button */}
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
                      src={recording ? "./close_white.svg" : "./speak.svg"}
                      loading="lazy"
                      alt="Mic"
                      className="h-full w-full p-2"
                    />
                  </div>
                  <span className="text-[#FFFFFF] text-[8px]">
                    {recording ? "Stop" : "Speak"}
                  </span>
                </div>
                {/* Text Input or Visualizer */}
                <div>
                  {recording ? (
                    <Visualizer
                      audio={audioStream}
                      mode={"continuous"}
                      autoStart={true}
                      strokeColor={"#131F49"}
                    >
                      {({ canvasRef }) => (
                        <canvas
                          ref={canvasRef}
                          className="h-12 xl:h-9 3xl:h-12 3xl:w-96 w-60 xl:w-40 2xl:w-64 bg-[#f2f2f22f] rounded"
                        />
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
                        alt="Send"
                        className="h-full w-full p-2"
                        loading="lazy"
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
    </div>
  );
};

export default ConversationLayout3;
