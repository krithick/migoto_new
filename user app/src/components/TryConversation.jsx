import React, { useEffect, useRef, useState } from "react";
import CoachVideoPlayer from "./CoachVideoPlayer";
import StreamingText from "./StreamingText";

const TryConversation = ({
  isThinking,
  conversation,
  setCoachMessage,
  language,
  mic,
  avatar,
  voice,
  finish,
  audioRef,
}) => {
  // Reference for conversation dialog
  const messagesEndRef = useRef();

  // Auto scroll for conversation dialog
  if (messagesEndRef.current) {
    messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
  }
  return (
    <div
      ref={messagesEndRef}
      className="h-full w-full overflow-y-auto [&::-webkit-scrollbar]:w-[3px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]"
    >
      <div className="w-full flex flex-col justify-between overflow-y-auto">
        {conversation &&
          conversation.map((value, index) => (
            <div
              className="flex flex-col gap-5 my-1.5 pl-2 pr-5 xl:pl-1 xl:pr-3 font-normal"
              key={index}
            >
              {value.role == "user" && (
                <>
                  {value?.correct == false ? (
                    <div className="flex justify-end">
                      <div className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] mr-1 bg-[#E31E1B] rounded-l-[15px] rounded-r-[5px] text-[12px]">
                        <div className="mr-1.5 py-1 px-4 bg-[#F4F4F4] rounded-l">
                          <div className="text-[12px] font-medium">
                            Executive
                          </div>
                          <div className="text-[10px] font-normal">
                            {value.message}
                          </div>
                          <div className="flex justify-end items-center text-[10px] gap-x-1 text-[#E31E1B]">
                            <span className="text-white bg-[#E31E1B] rounded-full h-3 w-3 flex justify-center items-center text-auto">
                              x
                            </span>
                            Incorrect
                          </div>
                        </div>
                      </div>
                      <img
                        loading="lazy"
                        src="./user_conversation.svg"
                        alt="user_conversation"
                        className="w-8 h-8 xl:w-6 xl:h-6 2xl:w-8 2xl:h-8 object-contain bg-[#131F49] p-1.5 rounded-full"
                      />
                    </div>
                  ) : (
                    <div className="flex justify-end">
                      <div className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] mr-2 py-1 px-4 bg-[#F4F4F4] rounded text-[12px]">
                        <div className="text-[12px] font-medium">Executive</div>
                        <div className="text-[10px] font-normal wrap-break-word">
                          {value.message}
                        </div>
                      </div>
                      <img
                        loading="lazy"
                        src="./user_conversation.svg"
                        alt="user_conversation"
                        className="w-8 h-8 xl:w-6 xl:h-6 2xl:w-8 2xl:h-8 object-contain bg-[#131F49] p-1.5 rounded-full"
                      />
                    </div>
                  )}
                </>
              )}

              {value.role == "bot" && (
                <>
                  {value?.correct != false ? (
                    <div className="flex justify-start">
                      <img
                        loading="lazy"
                        src="./user_conversation.svg"
                        alt="user_conversation"
                        className="w-8 h-8 xl:w-6 xl:h-6 2xl:w-8 2xl:h-8 object-contain bg-[#131F49] p-1.5 rounded-full"
                      />
                      <div className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] ml-2 py-1 px-4 bg-[#DFE8FF] rounded text-[12px]">
                        <div className="text-[12px] font-medium">
                          {avatar?.persona_id[0]?.name}
                        </div>
                        <div className="text-[10px] font-normal">
                          {value?.stream ? (
                            <StreamingText
                              message={value.message}
                              audioRef={audioRef}
                              mic={mic}
                            />
                          ) : (
                            <span>
                              {value.message.replace(/[\*\#]|\[CORRECT\]/g, "")}
                            </span>
                          )}
                        </div>

                        {/* <div className="text-[10px] font-normal">
                          {() => {
                            const words = value.message.split(" ");
                            audioRef?.current?.addEventListener(
                              "loadedmetadata",
                              () => {
                                const timePerWord =
                                  audioRef.current.duration / words.length;
                                console.log(
                                  "TCL: audioRef.current.onloadedmetadata -> timePerWord",
                                  timePerWord
                                );

                                words.forEach((_, i) => {
                                  setTimeout(() => {
                                    // setCurrentIndex(i);
                                    console.log("TCL: i", i);
                                  }, i * timePerWord * 1000);
                                });
                              }
                            );
                            return (
                              <span>
                                {value.message.replace(
                                  /[\*\#]|\[CORRECT\]/g,
                                  ""
                                )}
                              </span>
                            );
                          }}
                          {value.message.replace(/[\*\#]|\[CORRECT\]/g, "")}
                        </div> */}
                      </div>
                    </div>
                  ) : (
                    <div className="flex justify-center ">
                      <div className="bg-[#C6C6C66E] p-3 rounded-[10px] space-y-1.5">
                        <div className="flex">
                          <img
                            loading="lazy"
                            src="./user_conversation.svg"
                            alt="user_conversation"
                            className="w-8 h-8 xl:w-6 xl:h-6 2xl:w-8 2xl:h-8 object-contain bg-[#131F49] p-1.5 rounded-full"
                          />
                          <div className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] ml-2 py-1 px-4 bg-[#ffffff9d] rounded text-[12px] border border-[#131f497c]">
                            <div className="text-[12px] font-medium">Coach</div>
                            <div className="text-[10px] font-normal">
                              {value.message.replace(/[\*\#]|\[CORRECT\]/g, "")}
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            setCoachMessage(
                              value.message.replace(/[\*\#]|\[CORRECT\]/g, "")
                            );
                          }}
                          className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] ml-10 xl:ml-8 2xl:ml-10 py-1.5 px-4 bg-[#EFF7FC] rounded text-[12px] border border-[#131f497c] cursor-pointer"
                        >
                          Replay
                        </button>
                      </div>
                    </div>
                    // <CoachVideoPlayer
                    //   message={value.message}
                    //   language={language}
                    //   setMic={setMic}
                    //   voice={voice}
                    //   avatar={avatar}
                    // />
                  )}
                </>
              )}
              <>
                {/* <div className="flex justify-end">
                  <div className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] mr-1 bg-[#E31E1B] rounded-l-[15px] rounded-r-[5px] text-[12px]">
                    <div className="mr-1.5 py-1 px-4 bg-[#F4F4F4] rounded-l">
                      <div className="text-[12px] font-medium">User</div>
                      <div className="text-[10px] font-normal">test</div>
                      <div className="flex justify-end items-center text-[10px] gap-x-1 text-[#E31E1B]">
                        <span className="text-white bg-[#E31E1B] rounded-full h-3 w-3 flex justify-center items-center text-auto">
                          x
                        </span>
                        Incorrect
                      </div>
                    </div>
                  </div>
                  <img
                    src="./user_conversation.svg"
                    alt="user_conversation"
                    className="w-8 h-8 xl:w-6 xl:h-6 2xl:w-8 2xl:h-8 object-contain bg-[#131F49] p-1.5 rounded-full"
                  />
                </div> */}
              </>
              <>
                {/* <CoachVideoPlayer
                  message={value.message}
                  language={language}
                  setMic={setMic}
                  avatar={avatar}
                /> */}
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
                          <div className="text-[10px] font-normal">test</div>
                        </div>
                      </div>
                      <button className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] ml-10 xl:ml-8 2xl:ml-10 py-1.5 px-4 bg-[#EFF7FC] rounded text-[12px] border border-[#131f497c]">
                        Replay
                      </button>
                    </div>
                  </div> */}
              </>
            </div>
          ))}
        {/* added */}
        {isThinking && (
          <div className="flex justify-start my-1.5 pl-2 pr-5 xl:pl-1 xl:pr-3">
            <img
              loading="lazy"
              src="./user_conversation.svg"
              alt="bot_avatar"
              className="w-8 h-8 xl:w-6 xl:h-6 2xl:w-8 2xl:h-8 object-contain bg-[#131F49] p-1.5 rounded-full"
            />
            <div className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] ml-2 py-1 px-4 bg-[#DFE8FF] rounded text-[12px]">
              <div className="text-[12px] font-medium">
                {avatar?.persona_id?.[0]?.name || "Assistant"}
              </div>
              <div className="text-[10px] font-normal flex items-center gap-1">
                <div className="flex space-x-1">
                  <div className="w-1 h-1 bg-[#131F49] rounded-full animate-bounce"></div>
                  <div
                    className="w-1 h-1 bg-[#131F49] rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-1 h-1 bg-[#131F49] rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
                <span className="ml-2">Thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TryConversation;
