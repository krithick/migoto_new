import HeaderMenu from "./components/HeaderMenu";
import AssignSideMenu from "./components/AssignSideMenu";
import FinishConversationButtons from "./components/FinishConversationButtons";
import { useNavigate } from "react-router";
import PDFReader from "./components/PDFReader";
import { useEffect, useState } from "react";
import instance from "./service";

const LearnModePDF = () => {
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
                        className={`bg-[#131f490f] w-[11rem] h-[2rem] 2xl:h-[2.5rem] px-4 text-[#535BA4] border-b-2 text-[12px] rounded items-center justify-center flex gap-x-3 cursor-pointer`}
                      >
                        <img
                          src={`./LearnBotConversation.svg`}
                          alt="BotConversation"
                          loading="lazy"
                        />
                        Bot Conversation
                      </button>
                      <button
                        onClick={() =>
                          navigate("/learn-mode-video", { replace: true })
                        }
                        className={`bg-[#131f490f] w-[11rem] h-[2rem] 2xl:h-[2.5rem] px-4 text-[#535BA4] border-b-2 text-[12px] rounded items-center justify-center flex gap-x-3 cursor-pointer`}
                      >
                        <img
                          src={`./LearnVideo.svg`}
                          alt="LearnPDF"
                          loading="lazy"
                        />
                        Video
                      </button>
                      <button
                        className={`bg-[#131f490f] w-[11rem] h-[2rem] 2xl:h-[2.5rem] px-4  border-b-4 border-b-[#E98A3C] text-[#E98A3C] text-[12px] rounded items-center justify-center flex gap-x-3 cursor-pointer`}
                      >
                        <img
                          src={`./LearnPDF_select.svg`}
                          alt="LearnPDF"
                          loading="lazy"
                        />
                        Document
                      </button>
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[40.8rem] xl:h-[25.5rem] 2xl:h-[40.8rem] w-full px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem] py-[15px] xl:py-[10px] 2xl:py-[15px]">
                  <div className="h-full w-full flex justify-center gap-x-[5rem] xl:gap-x-[1rem] 2xl:gap-x-[3rem]">
                    <div className="h-[35rem] xl:h-[24rem] 2xl:h-[37.5rem] w-[25rem] xl:w-[14rem] 2xl:w-[20rem] bg-[#FFFFFF8F] rounded-[10px]">
                      <div className="h-[3rem] w-full flex items-center px-3 text-[#FFFFFF] text-[14px] rounded-t-[10px] bg-[#131F49]">
                        Document
                      </div>
                      <div className="h-[34rem] xl:h-[21rem] 2xl:h-[34rem] w-full pr-2 py-2 space-y-3 ">
                        <div className="h-full w-full px-2 space-y-2 overflow-y-auto [&::-webkit-scrollbar]:w-[3px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                          {pdfDetails &&
                            pdfDetails.map((value, index) => (
                              <div
                                key={index}
                                className="h-[6rem] w-full p-2 space-x-2 flex items-center rounded-[10px] bg-[#FFFFFF] border border-[#7070706E]"
                              >
                                <img
                                  loading="lazy"
                                  src={
                                    selectedPDF?.id == value.id
                                      ? "./LearnPDF_select.svg"
                                      : "./LearnPDF.svg"
                                  }
                                  alt={value?.title}
                                  className="h-[3rem] w-auto object-contain"
                                />
                                <div className="space-y-1.5 w-full">
                                  <p className="text-[#131F49] text-[12px] xl:text-[10px] font-medium">
                                    {value?.title}
                                  </p>
                                  <p className="text-[#707070] text-[10px] xl:text-[8px] font-normal line-clamp-2">
                                    {value?.description}
                                  </p>
                                  <div
                                    onClick={() => setSelectedPDF(value)}
                                    className="flex justify-end text-[#F68D1E] text-[12px] xl:text-[10px] underline cursor-pointer"
                                  >
                                    {selectedPDF?.id == value.id
                                      ? "Opened"
                                      : "Open"}
                                  </div>
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                    <div className="h-[35rem] xl:h-[24rem] 2xl:h-[37.5rem] w-[25rem] xl:w-[40rem] 2xl:w-[55rem] bg-[#FFFFFF8F] rounded-[10px]">
                      <div className="h-[3rem] w-full flex items-center px-3 text-[#FFFFFF] text-[14px] rounded-t-[10px] bg-[#131F49]">
                        Document Title
                      </div>
                      <div className="h-[34rem] xl:h-[10rem] 2xl:h-[34rem] w-full pr-2 py-2 space-y-3 ">
                        <div className="text-[#131F49] text-[14px] xl:text-[12px] 2xl:text-[14px] px-5">
                          Document Title
                        </div>
                        <div className="flex justify-center h-[31rem] xl:h-[18.5rem] 2xl:h-[31.8rem] rounded-b-[10px] w-full overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px] ">
                          {selectedPDF && (
                            <PDFReader pdf={selectedPDF.file_url} />
                          )}
                        </div>
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

export default LearnModePDF;
