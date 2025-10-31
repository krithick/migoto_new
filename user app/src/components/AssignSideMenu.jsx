import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const AssignSideMenu = ({ index, close, setClose }) => {
  useEffect(() => {
    FetchDatas();
  }, [index]);

  useEffect(() => {
    if (!close) {
      setTimeout(() => {
        setViewBlock(false);
      }, 1000);
    } else {
      setViewBlock(true);
    }
  }, [close]);
  // Store User selected data's
  const [course, setCourse] = useState(null);
  const [viewBlock, setViewBlock] = useState(false);
  const [module, setModule] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [mode, setMode] = useState(null);

  const [avatar, setAvatar] = useState(null);
  const [language, setLanguage] = useState(null);
  const [voice, setVoice] = useState(null);
  const [environment, setEnvironment] = useState(null);
  // Fetch Selected datas from localstorage
  const FetchDatas = () => {
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
  let navigate = useNavigate();
  return (
    <div
      className={`transition-all duration-700 ease-in-out delay-1000 h-full w-full ${
        viewBlock ? "hidden" : "block"
      }`}
    >
      <div className="h-[4rem] xl:h-[2.5rem] 2xl:h-[4rem] w-full flex justify-center items-center text-[#3E4580] text-[16px] xl:text-[14px] 2xl:text-[16px] font-medium px-3">
        <div className="flex flex-auto justify-center">Progress Details</div>
        {index == 11 && (
          <div className="has-tooltip">
            <span className="tooltip p-1 mt-6 text-[12px] rounded bg-[#131f4928] border border-[#FFFFFF]">
              Progress Bar
            </span>
            <img
              loading="lazy"
              onClick={() => setClose(true)}
              src="./menu.svg"
              alt="menu"
              className="bg-[#131f4928] border border-[#FFFFFF] p-1.5 cursor-pointer"
            />
          </div>
        )}
      </div>
      <hr className="text-[#131f4946] h-0" />
      <div className="h-[45rem] xl:h-[27rem] 2xl:h-[45rem] w-full py-2 2xl:py-4 px-2">
        <div className="h-full w-hull overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
          <div className="h-auto w-auto flex justify-center items-center">
            <div>
              <div className="flex gap-x-3">
                <div
                  className={`relative after:absolute after:start-3 after:top-5 after:bottom-0 after:w-px after:-translate-x-[0.5px] last:after:hidden ${
                    index == 1
                      ? "after:bg-[#929292]"
                      : index == 11
                      ? "after:bg-[#929292]"
                      : "after:bg-[#535BA4] transition-all duration-100 ease-in-out"
                  }`}
                >
                  <div className="relative z-10 flex items-center justify-center">
                    <div
                      className={`h-6 w-6 rounded-full flex justify-center items-center text-[12px] transform transition-all duration-100 ease-in-out ${
                        index == 1
                          ? "bg-[#C8D5FF] border border-[#34478B] text-[#34478B]"
                          : index == 11
                          ? "border border-[#929292] text-[#929292]"
                          : "bg-[#D2ECDA] border border-[#28A745] text-[#28A745]"
                      }`}
                    >
                      1
                    </div>
                  </div>
                </div>
                <div className="h-18 w-[10rem] 2xl:h-22 2xl:w-[12rem]  grow pt-0.5 pb-8">
                  <h3
                    onClick={() => {
                      if (index != 11 && index != 5) {
                        localStorage.removeItem("migoto-module");
                        localStorage.removeItem("migoto-scenario");
                        localStorage.removeItem("migoto-mode");
                        localStorage.removeItem("migoto-avatar");
                        localStorage.removeItem("migoto-language");
                        localStorage.removeItem("migoto-voice");
                        localStorage.removeItem("migoto-environment");
                        localStorage.setItem("migoto-url", "/assigned-course");
                        navigate("/assigned-course", { replace: true });
                      }
                    }}
                    className={`flex gap-x-1.5 text-[14px] xl:text-[12px] 2xl:text-[14px] cursor-default ${
                      index == 1
                        ? "text-[#34478B] cursor-pointer"
                        : index == 11
                        ? "text-[#929292]"
                        : "text-[#27A745] cursor-pointer"
                    } `}
                  >
                    <img
                      loading="lazy"
                      src={
                        index == 1
                          ? "./courses_current.svg"
                          : index == 11
                          ? "./courses.svg"
                          : "./courses_done.svg"
                      }
                      alt="courses"
                    />
                    Course
                  </h3>
                  <h3
                    className={`flex text-[12px] xl:text-[10px] 2xl:text-[12px] line-clamp-2 h-[90%] w-auto ${
                      index > 1 && index != 11
                        ? "text-[#27A745] cursor-pointer"
                        : index == 1
                        ? "text-[#34478B] cursor-pointer"
                        : "text-[#929292]"
                    }`}
                  >
                    {course?.title}
                  </h3>
                </div>
              </div>
              <div className="flex gap-x-3">
                <div
                  className={`relative after:absolute after:start-3 after:top-5 after:bottom-0 after:w-px after:-translate-x-[0.5px] last:after:hidden ${
                    index > 2 && index != 11
                      ? "after:bg-[#535BA4] transition-all duration-100 ease-in-out"
                      : "after:bg-[#929292]"
                  }`}
                >
                  <div className="relative z-10 flex items-center justify-center">
                    <div
                      className={`h-6 w-6 rounded-full flex justify-center items-center text-[12px]  transform transition-all duration-100 ease-in-out ${
                        index > 2 && index != 11
                          ? "scale-100 bg-[#D2ECDA] border border-[#28A745] text-[#28A745]"
                          : index == 2
                          ? "scale-110 bg-[#C8D5FF] border border-[#34478B] text-[#34478B]"
                          : "scale-90 border border-[#929292] text-[#929292]"
                      }`}
                    >
                      2
                    </div>
                  </div>
                </div>
                <div className="h-18 w-[10rem] 2xl:h-22 2xl:w-[12rem] grow pt-0.5 pb-8">
                  <h3
                    onClick={() => {
                      if (index != 11 && index != 5 && index > 2) {
                        localStorage.removeItem("migoto-scenario");
                        localStorage.removeItem("migoto-mode");
                        localStorage.removeItem("migoto-avatar");
                        localStorage.removeItem("migoto-language");
                        localStorage.removeItem("migoto-voice");
                        localStorage.removeItem("migoto-environment");
                        localStorage.setItem("migoto-url", "/assigned-module");
                        navigate("/assigned-module", { replace: true });
                      }
                    }}
                    className={`flex gap-x-1.5 text-[14px] xl:text-[12px] 2xl:text-[14px] ${
                      index > 2 && index != 11
                        ? "text-[#27A745] cursor-pointer"
                        : index == 2
                        ? "text-[#34478B] cursor-pointer"
                        : "text-[#929292]"
                    } `}
                  >
                    <img
                      loading="lazy"
                      src={
                        index > 2 && index != 11
                          ? "./modules_done.svg"
                          : index == 2
                          ? "./modules_current.svg"
                          : "./modules.svg"
                      }
                      alt="module"
                    />
                    Module
                  </h3>
                  <h3
                    className={`flex text-[12px] xl:text-[10px] 2xl:text-[12px] line-clamp-2 h-[90%] w-auto ${
                      index > 2 && index != 11
                        ? "text-[#27A745] cursor-pointer"
                        : index == 2
                        ? "text-[#34478B] cursor-pointer"
                        : "text-[#929292]"
                    }`}
                  >
                    {module?.title}
                  </h3>
                </div>
              </div>
              <div className="flex gap-x-3">
                <div
                  className={`relative after:absolute after:start-3 after:top-5 after:bottom-0 after:w-px after:-translate-x-[0.5px] last:after:hidden ${
                    index > 3 && index != 11
                      ? "after:bg-[#535BA4] transition-all duration-100 ease-in-out"
                      : "after:bg-[#929292]"
                  }`}
                >
                  <div className="relative z-10 flex items-center justify-center">
                    <div
                      className={`h-6 w-6 rounded-full flex justify-center items-center text-[12px]  transform transition-all duration-100 ease-in-out ${
                        index > 3 && index != 11
                          ? "scale-100 bg-[#D2ECDA] border border-[#28A745] text-[#28A745]"
                          : index == 3
                          ? "scale-110 bg-[#C8D5FF] border border-[#34478B] text-[#34478B]"
                          : "scale-90 border border-[#929292] text-[#929292]"
                      }`}
                    >
                      3
                    </div>
                  </div>
                </div>
                <div className="h-18 w-[10rem] 2xl:h-22 2xl:w-[12rem] grow pt-0.5 pb-8">
                  <h3
                    onClick={() => {
                      if (index != 11 && index != 5 && index > 3) {
                        localStorage.removeItem("migoto-mode");
                        localStorage.removeItem("migoto-avatar");
                        localStorage.removeItem("migoto-language");
                        localStorage.removeItem("migoto-voice");
                        localStorage.removeItem("migoto-environment");
                        localStorage.setItem(
                          "migoto-url",
                          "/assigned-scenario"
                        );
                        navigate("/assigned-scenario", { replace: true });
                      }
                    }}
                    className={`flex gap-x-1.5 text-[14px] xl:text-[12px] 2xl:text-[14px] ${
                      index > 3 && index != 11
                        ? "text-[#27A745] cursor-pointer"
                        : index == 3
                        ? "text-[#34478B] cursor-pointer"
                        : "text-[#929292]"
                    } `}
                  >
                    <img
                      loading="lazy"
                      src={
                        index > 3 && index != 11
                          ? "./scenario_done.svg"
                          : index == 3
                          ? "./scenario_current.svg"
                          : "./scenario.svg"
                      }
                      alt="scenario"
                    />
                    Scenario
                  </h3>
                  <h3
                    className={`flex text-[12px] xl:text-[10px] 2xl:text-[12px] line-clamp-2 h-[90%] w-auto ${
                      index > 3 && index != 11
                        ? "text-[#27A745] cursor-pointer"
                        : index == 3
                        ? "text-[#34478B] cursor-pointer"
                        : "text-[#929292]"
                    }`}
                  >
                    {scenario?.title}
                  </h3>
                </div>
              </div>
              <div className="flex gap-x-3">
                <div className="relative">
                  <div className="relative z-10 flex items-center justify-center">
                    <div
                      className={`h-6 w-6 rounded-full flex justify-center items-center text-[12px] transform transition-all duration-100 ease-in-out ${
                        index > 4 && index != 11
                          ? "bg-[#D2ECDA] border border-[#28A745] text-[#28A745]"
                          : index == 4
                          ? "bg-[#C8D5FF] border border-[#34478B] text-[#34478B]"
                          : "border border-[#929292] text-[#929292]"
                      }`}
                    >
                      4
                    </div>
                  </div>
                </div>
                <div className="h-14 w-[10rem] grow pt-0.5 pb-8">
                  <h3
                    onClick={() => {
                      if (index != 11 && index != 5 && index > 4) {
                        localStorage.removeItem("migoto-avatar");
                        localStorage.removeItem("migoto-language");
                        localStorage.removeItem("migoto-voice");
                        localStorage.removeItem("migoto-environment");
                        localStorage.setItem("migoto-url", "/assigned-mode");
                        navigate("/assigned-mode", { replace: true });
                      }
                    }}
                    className={`flex gap-x-1.5 text-[14px] xl:text-[12px] 2xl:text-[14px] ${
                      index > 4 && index != 11
                        ? "text-[#27A745] cursor-pointer"
                        : index == 4
                        ? "text-[#34478B] cursor-pointer"
                        : "text-[#929292]"
                    } `}
                  >
                    <img
                      loading="lazy"
                      src={
                        index > 4 && index != 11
                          ? "./mode_done.svg"
                          : index == 4
                          ? "./mode_current.svg"
                          : "./mode.svg"
                      }
                      alt="mode"
                    />
                    Mode
                  </h3>
                  <h3
                    className={`flex text-[12px] xl:text-[10px] 2xl:text-[12px] line-clamp-2 h-[90%] w-auto ${
                      index > 4 && index != 11
                        ? "text-[#27A745] cursor-pointer"
                        : index == 4
                        ? "text-[#34478B] cursor-pointer"
                        : "text-[#929292]"
                    }`}
                  >
                    {mode?.title}
                  </h3>
                </div>
              </div>
            </div>
          </div>
          {index > 5 && (
            <>
              <hr className="text-[#131f4946] h-0" />
              <div className="h-auto w-full flex justify-center items-center py-2 2xl:py-4 px-2">
                <div>
                  <div className="flex gap-x-3">
                    <div
                      className={`relative after:absolute after:start-3 after:top-5 after:bottom-0 after:w-px after:-translate-x-[0.5px] last:after:hidden ${
                        (index > 6) & (index != 11)
                          ? "after:bg-[#535BA4] transition-all duration-100 ease-in-out"
                          : "after:bg-[#929292]"
                      }`}
                    >
                      <div className="relative z-10 flex items-center justify-center">
                        <div
                          className={`h-6 w-6 rounded-full flex justify-center items-center text-[12px]  transform transition-all duration-100 ease-in-out ${
                            (index > 6) & (index != 11)
                              ? "bg-[#D2ECDA] border border-[#28A745] text-[#28A745]"
                              : index == 6
                              ? "bg-[#C8D5FF] border border-[#34478B] text-[#34478B]"
                              : "border border-[#929292] text-[#929292]"
                          }`}
                        >
                          1
                        </div>
                      </div>
                    </div>
                    <div className="h-18 w-[10rem] 2xl:h-22 2xl:w-[12rem] grow pt-0.5 pb-8">
                      <h3
                        onClick={() => {
                          if (index != 11 && index > 6) {
                            localStorage.removeItem("migoto-language");
                            localStorage.removeItem("migoto-voice");
                            localStorage.removeItem("migoto-environment");
                            localStorage.setItem(
                              "migoto-url",
                              "/assigned-avatar"
                            );
                            navigate("/assigned-avatar", { replace: true });
                          }
                        }}
                        className={`flex text-[14px] xl:text-[12px] 2xl:text-[14px] gap-x-1.5 ${
                          (index > 6) & (index != 11)
                            ? "text-[#27A745] cursor-pointer"
                            : index == 6
                            ? "text-[#34478B] cursor-pointer"
                            : "text-[#929292]"
                        } `}
                      >
                        <img
                          loading="lazy"
                          src={
                            index > 6 && index != 11
                              ? "./avatar_done.svg"
                              : index == 6
                              ? "./avatar_current.svg"
                              : "./avatar.svg"
                          }
                          alt="avatar"
                        />
                        Avatar
                      </h3>
                      <h3
                        className={`flex text-[12px] xl:text-[10px] 2xl:text-[12px] line-clamp-2 h-[90%] w-auto ${
                          (index > 6) & (index != 11)
                            ? "text-[#27A745] cursor-pointer"
                            : index == 6
                            ? "text-[#34478B] cursor-pointer"
                            : "text-[#929292]"
                        }`}
                      >
                        {avatar?.selected?.persona_id[0]?.name}
                      </h3>
                    </div>
                  </div>
                  <div className="flex gap-x-3">
                    <div
                      className={`relative after:absolute after:start-3 after:top-5 after:bottom-0 after:w-px after:-translate-x-[0.5px] last:after:hidden ${
                        (index > 7) & (index != 11)
                          ? "after:bg-[#535BA4] transition-all duration-100 ease-in-out"
                          : "after:bg-[#929292]"
                      }`}
                    >
                      <div className="relative z-10 flex items-center justify-center">
                        <div
                          className={`h-6 w-6 rounded-full flex justify-center items-center text-[12px]  transform transition-all duration-100 ease-in-out ${
                            (index > 7) & (index != 11)
                              ? "bg-[#D2ECDA] border border-[#28A745] text-[#28A745]"
                              : index == 7
                              ? "bg-[#C8D5FF] border border-[#34478B] text-[#34478B]"
                              : "border border-[#929292] text-[#929292]"
                          }`}
                        >
                          2
                        </div>
                      </div>
                    </div>
                    <div className="h-18 w-[10rem] 2xl:h-22 2xl:w-[12rem] grow pt-0.5 pb-8">
                      <h3
                        onClick={() => {
                          if (index != 11 && index > 7) {
                            localStorage.removeItem("migoto-voice");
                            localStorage.removeItem("migoto-environment");
                            localStorage.setItem(
                              "migoto-url",
                              "/assigned-language"
                            );
                            navigate("/assigned-language", { replace: true });
                          }
                        }}
                        className={`flex text-[14px] xl:text-[12px] 2xl:text-[14px] gap-x-1.5 ${
                          (index > 7) & (index != 11)
                            ? "text-[#27A745] cursor-pointer"
                            : index == 7
                            ? "text-[#34478B] cursor-pointer"
                            : "text-[#929292]"
                        } `}
                      >
                        <img
                          loading="lazy"
                          src={
                            index > 7 && index != 11
                              ? "./language_done.svg"
                              : index == 7
                              ? "./language_current.svg"
                              : "./language.svg"
                          }
                          alt="language"
                        />
                        Language
                      </h3>
                      <h3
                        className={`flex text-[12px] xl:text-[10px] 2xl:text-[12px] line-clamp-2 h-[90%] w-auto ${
                          (index > 7) & (index != 11)
                            ? "text-[#27A745] cursor-pointer"
                            : index == 7
                            ? "text-[#34478B] cursor-pointer"
                            : "text-[#929292]"
                        }`}
                      >
                        {language?.name}
                      </h3>
                    </div>
                  </div>
                  <div className="flex gap-x-3">
                    <div
                      className={`relative after:absolute after:start-3 after:top-5 after:bottom-0 after:w-px after:-translate-x-[0.5px] last:after:hidden ${
                        (index > 8) & (index != 11)
                          ? "after:bg-[#535BA4] transition-all duration-100 ease-in-out"
                          : "after:bg-[#929292]"
                      }`}
                    >
                      <div className="relative z-10 flex items-center justify-center">
                        <div
                          className={`h-6 w-6 rounded-full flex justify-center items-center text-[12px]  transform transition-all duration-100 ease-in-out ${
                            (index > 8) & (index != 11)
                              ? "bg-[#D2ECDA] border border-[#28A745] text-[#28A745]"
                              : index == 8
                              ? "bg-[#C8D5FF] border border-[#34478B] text-[#34478B]"
                              : "border border-[#929292] text-[#929292]"
                          }`}
                        >
                          3
                        </div>
                      </div>
                    </div>
                    <div className="h-18 w-[10rem] 2xl:h-22 2xl:w-[12rem] grow pt-0.5 pb-8">
                      <h3
                        onClick={() => {
                          if (index != 11 && index > 8) {
                            localStorage.removeItem("migoto-environment");
                            localStorage.setItem(
                              "migoto-url",
                              "/assigned-botvoice"
                            );
                            navigate("/assigned-botvoice", { replace: true });
                          }
                        }}
                        className={`flex text-[14px] xl:text-[12px] 2xl:text-[14px] gap-x-1.5 ${
                          (index > 8) & (index != 11)
                            ? "text-[#27A745] cursor-pointer"
                            : index == 8
                            ? "text-[#34478B] cursor-pointer"
                            : "text-[#929292]"
                        } `}
                      >
                        <img
                          loading="lazy"
                          src={
                            index > 8 && index != 11
                              ? "./voice_done.svg"
                              : index == 8
                              ? "./voice_current.svg"
                              : "./voice.svg"
                          }
                          alt="voice"
                        />
                        Voice
                      </h3>
                      <h3
                        className={`flex text-[12px] xl:text-[10px] 2xl:text-[12px] line-clamp-2 h-[90%] w-auto ${
                          (index > 8) & (index != 11)
                            ? "text-[#27A745] cursor-pointer"
                            : index == 8
                            ? "text-[#34478B] cursor-pointer"
                            : "text-[#929292]"
                        }`}
                      >
                        {voice?.name}
                      </h3>
                    </div>
                  </div>
                  <div className="flex gap-x-3">
                    <div className="relative">
                      <div className="relative z-10 flex items-center justify-center">
                        <div
                          className={`h-6 w-6 rounded-full flex justify-center items-center text-[12px] transform transition-all duration-100 ease-in-out ${
                            (index > 9) & (index != 11)
                              ? "bg-[#D2ECDA] border border-[#28A745] text-[#28A745]"
                              : index == 9
                              ? "bg-[#C8D5FF] border border-[#34478B] text-[#34478B]"
                              : "border border-[#929292] text-[#929292]"
                          }`}
                        >
                          4
                        </div>
                      </div>
                    </div>
                    <div className="h-10 w-[10rem] grow pt-0.5 pb-8">
                      <h3
                        onClick={() => {
                          if (index != 11 && index > 9) {
                            localStorage.setItem(
                              "migoto-url",
                              "/assigned-environment"
                            );
                            navigate("/assigned-environment", {
                              replace: true,
                            });
                          }
                        }}
                        className={`flex text-[14px] xl:text-[12px] 2xl:text-[14px] gap-x-1.5 ${
                          (index > 9) & (index != 11)
                            ? "text-[#27A745] cursor-pointer"
                            : index == 9
                            ? "text-[#34478B] cursor-pointer"
                            : "text-[#929292]"
                        } `}
                      >
                        <img
                          loading="lazy"
                          src={
                            index > 9 && index != 11
                              ? "./environment_done.svg"
                              : index == 9
                              ? "./environment_current.svg"
                              : "./environment.svg"
                          }
                          alt="environment"
                        />
                        Environment
                      </h3>
                      <h3
                        className={`flex text-[12px] xl:text-[10px] 2xl:text-[12px] ${
                          (index > 9) & (index != 11)
                            ? "text-[#27A745] cursor-pointer"
                            : index == 9
                            ? "text-[#34478B] cursor-pointer"
                            : "text-[#929292]"
                        }`}
                      >
                        {environment?.name}
                      </h3>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AssignSideMenu;
