import React, { useEffect, useState } from "react";
import AssignSideMenu from "./components/AssignSideMenu";
import HeaderMenu from "./components/HeaderMenu";
import { useNavigate } from "react-router";
import toast from "react-hot-toast";
import instance from "./service";
import { useFormattedDate } from "./hooks/useFormattedDate";
import ScenarioInfo from "./components/ScenarioInfo";

const AssignedScenarios = () => {
  const [module, setModule] = useState(null);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("");
  const [scenarioDetails, setScenarioDetails] = useState(null);
  const [reload, setReload] = useState(false);
  const [scenarioInfo, setScenarioInfo] = useState(false);
  const [scenarioInfoDetails, setScenarioInfoDetails] = useState(null);

  let navigate = useNavigate();

  const SelectionFunction = (props) => {
    if (selected == null) {
      setSelected(props);
    } else {
      if (selected.id == props.id) {
        setSelected(null);
      } else {
        setSelected(props);
      }
    }
  };
  const NavigateFunction = () => {
    if (selected != null) {
      localStorage.setItem(
        "migoto-scenario",
        JSON.stringify({
          title: selected.title,
          description: selected.description,
          id: selected.id,
          thumbnail_url: selected.thumbnail_url,
          assess_mode: selected.assess_mode,
          learn_mode: selected.learn_mode,
          try_mode: selected.try_mode,
          assigned_modes: selected.assigned_modes,
        })
      );
      localStorage.setItem("migoto-url", "/assigned-mode");
      navigate("/assigned-mode", { replace: true });
    } else {
      toast.error("Please select scenario");
    }
  };

  useEffect(() => {
    if (localStorage.getItem("migoto-token") == null) {
      navigate("/login", { replace: true });
    }
    if (localStorage.getItem("migoto-scenario") != null) {
      const course = JSON.parse(localStorage.getItem("migoto-scenario"));
      setSelected(course);
    }
    // Call the function to fetch assigned scenarios
    fetchAssignedscenarios();
  }, [reload]);

  // fetch assigned scenarios
  const fetchAssignedscenarios = async () => {
    try {
      let moduleID;
      if (localStorage.getItem("migoto-module") != null) {
        moduleID = JSON.parse(localStorage.getItem("migoto-module"));
        setModule(moduleID);
      }
      // Fetch and load token
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
      };
      instance
        .get(`/modules/${moduleID?.id}/scenarios`, { headers })
        .then((response) => {
          setScenarioDetails(response.data);
          if (selected == null) setSelected(response.data[0]);
        })
        .catch((error) => {
          console.error("Error fetching assigned scenario:", error);
        });
    } catch (error) {
      console.error("Error fetching assigned scenario:", error);
    }
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
              {module && module.title}
            </div>
            <div className="h-full w-full bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px] flex">
              <div className="h-full w-[80rem]">
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <div className="flex flex-auto justify-start">
                    <div>
                      <div className="flex items-center space-x-[10px]">
                        <img
                          src="./scenario_current.svg"
                          alt="scenario"
                          loading="lazy"
                          className="h-auto w-auto xl:h-[14px] 2xl:h-auto object-contain"
                        />
                        <span className="text-[16px] xl:text-[14px] 2xl:text-[16px] text-[#131F49]">
                          Scenarios
                        </span>
                      </div>
                      <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#131F49]">
                        Assigned Scenarios: {scenarioDetails?.length}
                      </div>
                    </div>
                  </div>
                  <div className="relative w-[247px] xl:w-[175px] 2xl:w-[247px]">
                    <input
                      type="text"
                      placeholder="Search"
                      onChange={(e) => setFilter(e.target.value)}
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
                    {scenarioDetails && scenarioDetails?.length == 0 && (
                      <>
                        <div className="h-full w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] bg-[#FFFFFF8F] rounded-[10px] justify-center items-center">
                          No available scenario, please contact to admin
                        </div>
                      </>
                    )}

                    {scenarioDetails &&
                      scenarioDetails.map((value, index) => (
                        <>
                          {filter != "" ? (
                            <>
                              {value.title.toLowerCase().includes(filter) ? (
                                <div
                                  key={index}
                                  className="h-[18rem] xl:h-[17rem] 2xl:h-[21.5rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-default"
                                >
                                  <div className="h-full w-full">
                                    {value.thumbnail_url == "string" ? (
                                      <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center text-center bg-amber-50">
                                        {value.title}
                                      </p>
                                    ) : (
                                      <img
                                        src={value.thumbnail_url}
                                        alt={value.title + index}
                                        loading="lazy"
                                        className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-fill rounded-t"
                                      />
                                    )}
                                    <div className="h-[50%] w-full">
                                      {/* Course title and description */}
                                      <div className="h-[4.8rem] xl:h-[4.8rem] 2xl:h-[6rem] w-full space-y-1">
                                        <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600] line-clamp-2">
                                          {value.title}
                                        </div>
                                        <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-2">
                                          {value.description}
                                        </div>
                                      </div>
                                      <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                                        <div className="w-full h-auto space-y-0.5">
                                          <div className="w-full h-auto flex text-[10px]">
                                            <div className="flex flex-auto text-[#0000008a]">
                                              {` Assigned on:
                                              ${useFormattedDate(
                                                value?.assigned_date
                                              )}`}
                                            </div>
                                            <div
                                              className="text-[#A4A029] underline cursor-pointer"
                                              onClick={() => {
                                                setScenarioInfo(!scenarioInfo);
                                                setScenarioInfoDetails(value);
                                              }}
                                            >
                                              View more...
                                            </div>
                                            {/* <div
                                              className={`${
                                                value.completed
                                                  ? "text-[#27A745]"
                                                  : "text-[#A4A029]"
                                              }`}
                                            >
                                              {value.completed
                                                ? "Completed"
                                                : "Yet to Start"}
                                            </div> */}
                                          </div>
                                          <button
                                            onClick={() =>
                                              SelectionFunction(value)
                                            }
                                            className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                              selected?.id == value.id
                                                ? "bg-[#F68D1E] text-[#EEF8FB] border border-[#F68D1E]"
                                                : "border border-[#F68D1E] text-[#F68D1E]"
                                            }`}
                                          >
                                            {selected?.id == value.id
                                              ? "Selected"
                                              : "Select"}
                                          </button>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              ) : null}
                            </>
                          ) : (
                            <div
                              key={index}
                              className="h-[18rem] xl:h-[17rem] 2xl:h-[21.5rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-default"
                            >
                              <div className="h-full w-full">
                                {value.thumbnail_url == "string" ? (
                                  <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center text-center bg-amber-50">
                                    {value.title}
                                  </p>
                                ) : (
                                  <img
                                    src={value.thumbnail_url}
                                    alt={value.title + index}
                                    loading="lazy"
                                    className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t"
                                  />
                                )}
                                <div className="h-[50%] w-full">
                                  {/* Course title and description */}
                                  <div className="h-[4.8rem] xl:h-[4.8rem] 2xl:h-[6rem] w-full space-y-1">
                                    <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600] line-clamp-2">
                                      {value.title}
                                    </div>
                                    <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-2">
                                      {value.description}
                                    </div>
                                  </div>
                                  <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.4rem] w-full flex items-end">
                                    <div className="w-full h-auto space-y-0.5">
                                      <div className="w-full h-auto flex text-[10px]">
                                        <div className="flex flex-auto text-[#0000008a]">
                                          {`Assigned on:
                                          ${useFormattedDate(
                                            value?.assigned_date
                                          )}`}
                                        </div>
                                        <div
                                          className="text-[#A4A029] underline cursor-pointer"
                                          onClick={() => {
                                            setScenarioInfo(!scenarioInfo);
                                            console.log(
                                              "TCL: scenarioInfo",
                                              scenarioInfo
                                            );
                                            setScenarioInfoDetails(value);
                                          }}
                                        >
                                          View more...
                                        </div>
                                        {/* <div
                                          className={`${
                                            value.completed
                                              ? "text-[#27A745]"
                                              : "text-[#A4A029]"
                                          }`}
                                        >
                                          {value.completed
                                            ? "Completed"
                                            : "Yet to Start"}
                                        </div> */}
                                      </div>
                                      <button
                                        onClick={() => SelectionFunction(value)}
                                        className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                          selected?.id == value.id
                                            ? "bg-[#F68D1E] text-[#EEF8FB] border border-[#F68D1E]"
                                            : "border border-[#F68D1E] text-[#F68D1E]"
                                        }`}
                                      >
                                        {selected?.id == value.id
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
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-between items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <button
                    onClick={() => {
                      localStorage.setItem("migoto-url", "/assigned-module");
                      navigate("/assigned-module", { replace: true });
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
                <AssignSideMenu index={3} />
              </div>
            </div>
          </div>
        </div>
        <ScenarioInfo
          scenarioInfo={scenarioInfo}
          setScenarioInfo={setScenarioInfo}
          scenarioInfoDetails={scenarioInfoDetails}
          setScenarioInfoDetails={setScenarioInfoDetails}
        />
      </div>
    </div>
  );
};

export default AssignedScenarios;
