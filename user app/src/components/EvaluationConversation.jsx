import React, { useRef } from "react";
import StreamingText from "./StreamingText";

const EvaluationConversation = ({
  isThinking,
  conversation,
  avatar,
  finish,
  language,
  audioRef,
  mic,
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
      <div className="w-full flex flex-col justify-between">
        {conversation &&
          conversation.map((value, index) => (
            <div
              className="flex flex-col gap-5 my-1.5 pl-2 pr-5 xl:pl-1 xl:pr-3 font-normal"
              key={index}
            >
              {value.role == "user" && (
                <div className="flex justify-end">
                  <div className="w-[16.5rem] xl:w-[11rem] 2xl:w-[16.5rem] mr-2 py-1 px-4 bg-[#F4F4F4] rounded text-[12px]">
                    <div className="text-[12px] font-medium">Executive</div>
                    <div className="text-[10px] font-normal wrap-break-word">
                      {value.message}
                    </div>
                  </div>
                  <img
                    src="./user_conversation.svg"
                    loading="lazy"
                    alt="user_conversation"
                    className="w-8 h-8 xl:w-6 xl:h-6 2xl:w-8 2xl:h-8 object-contain bg-[#131F49] p-1.5 rounded-full"
                  />
                </div>
              )}
              {value.role == "bot" && (
                <>
                  {value?.correct != false && (
                    <div className="flex justify-start">
                      <img
                        src="./user_conversation.svg"
                        alt="user_conversation"
                        loading="lazy"
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
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          ))}
        {/* added */}
        {isThinking && (
          <div className="flex justify-start my-1.5 pl-2 pr-5 xl:pl-1 xl:pr-3">
            <img
              src="./user_conversation.svg"
              loading="lazy"
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

export default EvaluationConversation;
