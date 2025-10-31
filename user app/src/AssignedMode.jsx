import React, { useEffect, useState } from "react";
import AssignSideMenu from "./components/AssignSideMenu";
import HeaderMenu from "./components/HeaderMenu";
import { useNavigate } from "react-router";
import toast from "react-hot-toast";

const AssignedMode = () => {
  const [selected, setSelected] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [reload, setReload] = useState(false);
  let navigate = useNavigate();

  const SelectionFunction = (props) => {
    if (selected == null) {
      setSelected(props);
    } else {
      if (selected?.title == props.title) {
        setSelected(null);
      } else {
        setSelected(props);
      }
    }
  };

  const NavigateFunction = () => {
    if (selected != null) {
      if (selected.title == "Learn Mode") {
        localStorage.setItem("migoto-url", "/learn-mode-bot");
        navigate("/learn-mode-bot", { replace: true });
      } else {
        localStorage.setItem("migoto-url", "/assigned-avatar");
        navigate("/assigned-avatar", { replace: true });
      }
      localStorage.setItem(
        "migoto-mode",
        JSON.stringify({
          title: selected.title,
          description: selected.description,
          avatar_interaction: selected.avatar_interaction,
          thumbnail: selected.thumbnail,
        })
      );
    } else {
      toast.error("Please select modes");
    }
  };

  useEffect(() => {
    if (localStorage.getItem("migoto-token") == null) {
      navigate("/login", { replace: true });
    }
    if (localStorage.getItem("migoto-scenario") != null) {
      setScenario(JSON.parse(localStorage.getItem("migoto-scenario")));
      let scenario = JSON.parse(localStorage.getItem("migoto-scenario"));
      if (localStorage.getItem("migoto-mode") == null) {
        if (scenario?.assigned_modes[0] == "learn_mode") {
          SelectionFunction({
            title: "Learn Mode",
            description:
              "Engage with and understand new concepts through interactive, guided learning experiences.",
            thumbnail: "./learnmode.png",
            avatar_interaction: scenario?.learn_mode.avatar_interaction,
          });
        }
        if (scenario?.assigned_modes[0] == "try_mode") {
          SelectionFunction({
            title: "Try Mode",
            description:
              "Engage with and understand new concepts through interactive, guided learning experiences.",
            thumbnail: "./trymode.png",
            avatar_interaction: scenario?.try_mode.avatar_interaction,
          });
        }
        if (scenario?.assigned_modes[0] == "assess_mode") {
          SelectionFunction({
            title: "Assess Mode",
            description:
              "Engage with and understand new concepts through interactive, guided learning experiences.",
            thumbnail: "./assesmode.png",
            avatar_interaction: scenario?.assess_mode.avatar_interaction,
          });
        }
      } else {
        // console.log("TCL: AssignedMode -> scenario", scenario);
        let Mode = JSON.parse(localStorage.getItem("migoto-mode"));
        // console.log("TCL: AssignedMode -> Mode", Mode.title);
        if (Mode?.title == "Learn Mode") {
          SelectionFunction({
            title: "Learn Mode",
            description:
              "Engage with and understand new concepts through interactive, guided learning experiences.",
            thumbnail: "./learnmode.png",
            avatar_interaction: scenario?.learn_mode.avatar_interaction,
          });
        }
        if (Mode?.title == "Try Mode") {
          SelectionFunction({
            title: "Try Mode",
            description:
              "Engage with and understand new concepts through interactive, guided learning experiences.",
            thumbnail: "./trymode.png",
            avatar_interaction: scenario?.try_mode.avatar_interaction,
          });
        }
        if (Mode?.title == "Assess Mode") {
          SelectionFunction({
            title: "Assess Mode",
            description:
              "Engage with and understand new concepts through interactive, guided learning experiences.",
            thumbnail: "./assesmode.png",
            avatar_interaction: scenario?.assess_mode.avatar_interaction,
          });
        }
        // SelectionFunction(JSON.parse(localStorage.getItem("migoto-mode")));
      }
    }
  }, [reload]);
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
              {scenario && scenario.title}
            </div>
            <div className="h-full w-full bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px] flex">
              <div className="h-full w-[80rem]">
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <div className="flex flex-auto justify-start">
                    <div>
                      <div className="flex items-center space-x-[10px]">
                        <img
                          src="./mode_current.svg"
                          loading="lazy"
                          alt="Mode"
                          className="h-auto w-auto xl:h-[14px] 2xl:h-auto object-contain"
                        />
                        <span className="text-[16px] xl:text-[14px] 2xl:text-[16px] text-[#131F49]">
                          Modes
                        </span>
                      </div>
                      <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#131F49]">
                        Assigned Modes: {scenario?.assigned_modes.length}
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
                    {scenario && scenario?.assigned_modes.length == 0 && (
                      <>
                        <div className="h-full w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] bg-[#FFFFFF8F] rounded-[10px] justify-center items-center">
                          No available modes, please contact to admin
                        </div>
                      </>
                    )}

                    {scenario &&
                      scenario.assigned_modes.map((value) => (
                        <>
                          {value === "learn_mode" && (
                            <div className="h-[18rem] xl:h-[15rem] 2xl:h-[18rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px]">
                              <div className="h-full w-full">
                                <img
                                  src="./learnmode.png"
                                  loading="lazy"
                                  alt="learnmode"
                                  className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t"
                                />
                                <div className="h-[45%] w-full">
                                  <div className="h-[4.4rem] xl:h-[3.75rem] 2xl:h-[4.4rem] w-full space-y-0.5">
                                    <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                      Learn Mode
                                    </div>
                                    <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal">
                                      Engage with and understand new concepts
                                      through interactive, guided learning
                                      experiences.
                                    </div>
                                  </div>
                                  <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                                    <div className="w-full h-auto space-y-0.5">
                                      <div className="w-full h-auto flex text-[10px]"></div>
                                      <button
                                        onClick={() =>
                                          SelectionFunction({
                                            title: "Learn Mode",
                                            description:
                                              "Engage with and understand new concepts through interactive, guided learning experiences.",
                                            thumbnail: "./learnmode.png",
                                            avatar_interaction:
                                              scenario?.learn_mode
                                                .avatar_interaction,
                                          })
                                        }
                                        className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                          selected?.title == "Learn Mode"
                                            ? "bg-[#F68D1E] text-[#EEF8FB] border border-[#F68D1E]"
                                            : "border border-[#F68D1E] text-[#F68D1E]"
                                        }`}
                                      >
                                        {selected?.title == "Learn Mode"
                                          ? "Selected"
                                          : "Select"}
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                          {value === "try_mode" && (
                            <div className="h-[18rem] xl:h-[15rem] 2xl:h-[18rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px]">
                              <div className="h-full w-full">
                                <img
                                  src="./trymode.png"
                                  loading="lazy"
                                  alt="learnmode"
                                  className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t"
                                />
                                <div className="h-[45%] w-full">
                                  <div className="h-[4.4rem] xl:h-[3.75rem] 2xl:h-[4.4rem] w-full space-y-0.5">
                                    <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                      Try Mode
                                    </div>
                                    <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal">
                                      Help users practice and refine skills
                                      through structured exercises and
                                      simulations.
                                    </div>
                                  </div>
                                  <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                                    <div className="w-full h-auto space-y-0.5">
                                      <div className="w-full h-auto flex text-[10px]"></div>
                                      <button
                                        onClick={() =>
                                          SelectionFunction({
                                            title: "Try Mode",
                                            description:
                                              "Help users practice and refine skills through structured exercises and simulations.",
                                            thumbnail: "./trymode.png",
                                            avatar_interaction:
                                              scenario?.try_mode
                                                .avatar_interaction,
                                          })
                                        }
                                        className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                          selected?.title == "Try Mode"
                                            ? "bg-[#F68D1E] text-[#EEF8FB] border border-[#F68D1E]"
                                            : "border border-[#F68D1E] text-[#F68D1E]"
                                        }`}
                                      >
                                        {selected?.title == "Try Mode"
                                          ? "Selected"
                                          : "Select"}
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                          {value === "assess_mode" && (
                            <div className="h-[18rem] xl:h-[15rem] 2xl:h-[18rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px]">
                              <div className="h-full w-full">
                                <img
                                  src="./assesmode.png"
                                  loading="lazy"
                                  alt="learnmode"
                                  className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t"
                                />
                                <div className="h-[45%] w-full">
                                  <div className="h-[4.4rem] xl:h-[3.75rem] 2xl:h-[4.4rem] w-full space-y-0.5">
                                    <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                      Assess Mode
                                    </div>
                                    <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal">
                                      Evaluates users' knowledge or performance
                                      through tests, quizzes, or challenges.
                                    </div>
                                  </div>
                                  <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                                    <div className="w-full h-auto space-y-0.5">
                                      <div className="w-full h-auto flex text-[10px]"></div>
                                      <button
                                        onClick={() =>
                                          SelectionFunction({
                                            title: "Assess Mode",
                                            description:
                                              "Evaluates users' knowledge or performance through tests, quizzes, or challenges.",
                                            thumbnail: "./assesmode.png",
                                            avatar_interaction:
                                              scenario?.assess_mode
                                                .avatar_interaction,
                                          })
                                        }
                                        className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                          selected?.title == "Assess Mode"
                                            ? "bg-[#F68D1E] text-[#EEF8FB] border border-[#F68D1E]"
                                            : "border border-[#F68D1E] text-[#F68D1E]"
                                        }`}
                                      >
                                        {selected?.title == "Assess Mode"
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

                    {/* {scenario && scenario.learn_mode.length != 0 && (
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[18rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px]">
                        <div className="h-full w-full">
                          <img
                            src="./learnmode.png"
                            alt="learnmode"
                            className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t"
                          />
                          <div className="h-[45%] w-full">
                            <div className="h-[4.4rem] xl:h-[3.75rem] 2xl:h-[4.4rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                Learn Mode
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal">
                                Engage with and understand new concepts through
                                interactive, guided learning experiences.
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                  Assigned on: {value.assignDate}
                                </div>
                                <div className="text-[#A4A029]">
                                  {value.status}
                                </div>
                                </div>
                                <button
                                  onClick={() =>
                                    SelectionFunction({
                                      title: "Learn Mode",
                                      description:
                                        "Engage with and understand new concepts through interactive, guided learning experiences.",
                                      thumbnail: "./learnmode.png",
                                      avatar_interaction:
                                        scenario?.learn_mode.avatar_interaction,
                                    })
                                  }
                                  className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                    selected?.title == "Learn Mode"
                                      ? "bg-[#F68D1E] text-[#EEF8FB] border border-[#F68D1E]"
                                      : "border border-[#F68D1E] text-[#F68D1E]"
                                  }`}
                                >
                                  {selected?.title == "Learn Mode"
                                    ? "Selected"
                                    : "Select"}
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    {scenario && scenario.try_mode.length != 0 && (
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[18rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px]">
                        <div className="h-full w-full">
                          <img
                            src="./trymode.png"
                            alt="learnmode"
                            className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t"
                          />
                          <div className="h-[45%] w-full">
                            <div className="h-[4.4rem] xl:h-[3.75rem] 2xl:h-[4.4rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                Try Mode
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal">
                                Help users practice and refine skills through
                                structured exercises and simulations.
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                  Assigned on: {value.assignDate}
                                </div>
                                <div className="text-[#A4A029]">
                                  {value.status}
                                </div>
                                </div>
                                <button
                                  onClick={() =>
                                    SelectionFunction({
                                      title: "Try Mode",
                                      description:
                                        "Help users practice and refine skills through structured exercises and simulations.",
                                      thumbnail: "./trymode.png",
                                      avatar_interaction:
                                        scenario?.try_mode.avatar_interaction,
                                    })
                                  }
                                  className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                    selected?.title == "Try Mode"
                                      ? "bg-[#F68D1E] text-[#EEF8FB] border border-[#F68D1E]"
                                      : "border border-[#F68D1E] text-[#F68D1E]"
                                  }`}
                                >
                                  {selected?.title == "Try Mode"
                                    ? "Selected"
                                    : "Select"}
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    {scenario && scenario.assess_mode.length != 0 && (
                      <div className="h-[18rem] xl:h-[15rem] 2xl:h-[18rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px]">
                        <div className="h-full w-full">
                          <img
                            src="./assesmode.png"
                            alt="learnmode"
                            className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t"
                          />
                          <div className="h-[45%] w-full">
                            <div className="h-[4.4rem] xl:h-[3.75rem] 2xl:h-[4.4rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                Assess Mode
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal">
                                Evaluates users' knowledge or performance
                                through tests, quizzes, or challenges.
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                  Assigned on: {value.assignDate}
                                </div>
                                <div className="text-[#A4A029]">
                                  {value.status}
                                </div>
                                </div>
                                <button
                                  onClick={() =>
                                    SelectionFunction({
                                      title: "Assess Mode",
                                      description:
                                        "Evaluates users' knowledge or performance through tests, quizzes, or challenges.",
                                      thumbnail: "./assesmode.png",
                                      avatar_interaction:
                                        scenario?.assess_mode
                                          .avatar_interaction,
                                    })
                                  }
                                  className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                    selected?.title == "Assess Mode"
                                      ? "bg-[#F68D1E] text-[#EEF8FB] border border-[#F68D1E]"
                                      : "border border-[#F68D1E] text-[#F68D1E]"
                                  }`}
                                >
                                  {selected?.title == "Assess Mode"
                                    ? "Selected"
                                    : "Select"}
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )} */}
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-between items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <button
                    onClick={() => {
                      localStorage.setItem("migoto-url", "/assigned-scenario");
                      navigate("/assigned-scenario", { replace: true });
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
                <AssignSideMenu index={4} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssignedMode;
