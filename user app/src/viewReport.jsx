import { useEffect, useState } from "react";
import HeaderMenu from "./components/HeaderMenu";
import toast from "react-hot-toast";
import instance from "./service";
import ViewReportModel from "./components/ViewReportModel";
import { useFormattedDate } from "./hooks/useFormattedDate";
import { useNavigate } from "react-router";
import { Baseurl } from "./route";

const ViewReport = () => {
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("");
  const [viewModel, setViewModel] = useState("report");
  const [scenarioName, setScenarioName] = useState("report");
  const [reload, setReload] = useState(false);
  const [ReportDetails, setReportDetails] = useState(null);

  const [reportModelView, setReportModelView] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingID, setLoadingID] = useState();
  let navigate = useNavigate();

  const NavigateFunction = (props) => {
    // if (selected != null) {
    setViewModel("report");
    setReportModelView(!reportModelView);
    setSelected(props);
    setScenarioName(props?.scenario_name);
    // } else {
    //   toast.error("Please select scenario");
    // }
  };

  const viewPersonalizeReportFunction = (props) => {
    setLoading(true);

    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("migoto-token")}`,
    };

    // Call POST API to generate the report
    instance
      .post(
        `chat/evaluate/${props?.session_id}`,
        {},
        { headers }
      )
      .then((response) => {
        setViewModel("personalize");
        setScenarioName(props?.scenario_name);
        setReportModelView(!reportModelView);
        setSelected(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error generating report:", error);
        setLoading(false);
      });
  };

  useEffect(() => {
    if (localStorage.getItem("migoto-token") == null) {
      navigate("/login", { replace: true });
    }
    FetchUserCourse();
  }, [reload]);

  function FetchUserCourse() {
    setLoading(true); // Set loading state to true
    let token = localStorage.getItem("migoto-token");
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ` + token,
    };
    instance
      .get("/auth/users/me/completed-scenario-analysis", { headers })
      .then((responce) => {
        setLoading(false); // Set loading state to true
        setReportDetails(responce.data);
      })
      .catch((error) => {
        setLoading(false); // Set loading state to true
        console.log("Error fetching completed report :", error);
      });
  }

  return (
    <div className="absolute inset-0 backdrop-blur-[68px]">
      <div className="relative h-screen w-screen">
        <HeaderMenu
          index={2}
          reload={reload}
          disable={true}
          setReload={setReload}
        />
        <div className="flex h-[35.5rem] w-screen items-center xl:h-[37.6rem] 2xl:h-[54rem]">
          <div className="h-full w-screen place-content-center px-[12rem] pb-[5rem] xl:px-[7.5rem] 2xl:px-[12rem]">
            <div className="flex h-[50px] items-center text-[16px] font-medium text-[#000000] xl:h-[40px] xl:text-[14px] 2xl:h-[50px] 2xl:text-[16px]">
              View Reports
            </div>
            <div className="flex h-full w-full rounded-l-[30px] rounded-r-[10px] bg-[#ffffff80]">
              <div className="h-full w-full">
                <div className="flex h-[5rem] w-full items-center px-[3.5rem] xl:h-[3rem] xl:px-[2rem] 2xl:h-[5rem] 2xl:px-[3.5rem]">
                  <div className="flex flex-auto justify-start">
                    <div className="flex items-center space-x-[10px]">
                      <span className="text-[16px] text-[#131F49] xl:text-[14px] 2xl:text-[16px]">
                        My report
                      </span>
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] h-0 text-[#131f4946] xl:mx-[2rem] 2xl:mx-[3.5rem]" />
                <div className="h-[38rem]  w-full py-[15px] pr-[22px] pl-[3.5rem] xl:h-[26rem] xl:py-[10px] xl:pr-[14px] xl:pl-[2rem] 2xl:h-[39rem] 2xl:py-[15px] 2xl:pr-[22px] 2xl:pl-[3.5rem]">
                  <div className="flex h-[3rem] w-full 2xl:pr-[22px]">
                    <div className="flex flex-auto">
                      <div className="text-[12px] text-[#131F49] xl:text-[10px] 2xl:text-[12px]">
                        Total Number of Reports:{" "}
                        {ReportDetails && ReportDetails.length}
                      </div>
                    </div>
                    <div className="relative flex w-[247px] items-center xl:w-[175px] 2xl:w-[247px]">
                      <input
                        type="text"
                        placeholder="Search"
                        onChange={(e) => setFilter(e.target.value)}
                        className="w-full rounded-[30px] bg-[#C7DFF0] py-2 pr-4 pl-10 text-[10px] text-[#000000] focus:outline-none 2xl:text-[12px]"
                      />
                      <div className="absolute top-1/2 left-3 -translate-y-1/2 text-gray-400">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-[12px] w-5 xl:h-[14px] 2xl:h-[14px]"
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
                  <div className="flex h-[33rem] xl:h-[21.5rem] 2xl:h-[38rem] w-full flex-wrap space-y-[36px] gap-x-[5rem] overflow-y-auto xl:gap-x-[2.5rem] 2xl:gap-x-[6rem] py-2 [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-thumb]:rounded-[22px] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef]">
                    {ReportDetails &&
                      ReportDetails.map((value, index) => (
                        <>
                          {filter != "" ? (
                            <>
                              {value.scenario_name
                                .toLowerCase()
                                .includes(filter) ? (
                                <div
                                  key={index}
                                  className="h-[15rem] w-[10rem] cursor-default rounded-[10px] bg-[#FFFFFF] p-[5px] xl:h-[13rem] xl:w-[18rem] 2xl:h-[16rem] 2xl:w-[18rem]"
                                >
                                  <div className="h-full w-full">
                                    {value.thumbnail_url == "string" ? (
                                      <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center bg-amber-50">
                                        {value?.scenario_name}
                                      </p>
                                    ) : (
                                      <img
                                        src={value?.thumbnail_url}
                                        alt={value?.scenario_name + index}
                                        loading="lazy"
                                        className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t"
                                      />
                                    )}

                                    <div className="h-[50%] w-full">
                                      <div className="h-[4rem] w-full space-y-0.5 xl:h-[3rem] 2xl:h-[3.5rem]">
                                        <div className="text-[16px] font-[600] text-[#000000] xl:text-[12px] 2xl:text-[16px]">
                                          {value.scenario_name}
                                        </div>
                                        <div className="text-[12px] font-normal text-[#0000008a] xl:text-[10px] 2xl:text-[12px]">
                                          {value.description}
                                        </div>
                                      </div>
                                      <div className="flex h-[3rem] w-full items-end xl:h-[3.2rem] 2xl:h-[3.4rem]">
                                        <div className="h-auto w-full space-y-0.5">
                                          <div className="flex h-auto w-full text-[10px]">
                                            <div className="flex flex-auto text-[#0000008a]">
                                              Assigned on:{" "}
                                              {useFormattedDate(
                                                value?.completed_date ?? ""
                                              )}
                                            </div>
                                            <div className={"text-[#27A745]"}>
                                              Completed
                                            </div>
                                          </div>
                                          <div className="flex space-x-2">
                                            <button
                                              onClick={() => {
                                                setLoadingID(index);
                                                viewPersonalizeReportFunction(
                                                  value
                                                );
                                              }}
                                              className={`flex h-auto w-full cursor-pointer justify-center rounded-[5px] py-2 text-[12px] xl:py-1.5 xl:text-[10px] 2xl:text-[12px] ${
                                                selected?.session_id ==
                                                value.session_id
                                                  ? "border border-[#F68D1E] bg-[#F68D1E] text-[#EEF8FB]"
                                                  : "border border-[#F68D1E] text-[#F68D1E]"
                                              }`}
                                            >
                                              {loading && loadingID == index
                                                ? "Please Wait"
                                                : selected?.session_id ==
                                                  value.session_id
                                                ? "Viewed"
                                                : "Personalize Report"}
                                            </button>
                                            <button
                                              onClick={() =>
                                                // SelectionFunction(value)
                                                NavigateFunction(value)
                                              }
                                              className={`flex h-auto w-full cursor-pointer justify-center rounded-[5px] py-2 text-[12px] xl:py-1.5 xl:text-[10px] 2xl:text-[12px] ${
                                                selected?.session_id ==
                                                value.session_id
                                                  ? "border border-[#F68D1E] bg-[#F68D1E] text-[#EEF8FB]"
                                                  : "border border-[#F68D1E] text-[#F68D1E]"
                                              }`}
                                            >
                                              View Report
                                            </button>
                                          </div>
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
                              className="h-[18rem] xl:h-[17rem] 2xl:h-[21.5rem] w-[21rem] xl:w-[20rem] 2xl:w-[24rem] p-[5px] bg-[#FFFFFF] rounded-[10px] cursor-default"
                            >
                              <div className="h-full w-full">
                                {value.thumbnail_url == "string" ? (
                                  <p className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full rounded-t flex justify-center items-center bg-amber-50">
                                    {value?.scenario_name}
                                  </p>
                                ) : (
                                  <img
                                    src={value?.thumbnail_url}
                                    alt={value?.scenario_name + index}
                                    loading="lazy"
                                    className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-cover rounded-t"
                                  />
                                )}
                                <div className="h-[50%] w-full">
                                  {/* Course title and description */}
                                  <div className="h-[4.8rem] xl:h-[4.8rem] 2xl:h-[6rem] w-full space-y-1">
                                    <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                      {value.scenario_name}
                                    </div>
                                    <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-2">
                                      {value.description}
                                    </div>
                                  </div>
                                  <div className="flex h-[3rem] w-full items-end xl:h-[3.2rem] 2xl:h-[3.4rem]">
                                    <div className="h-auto w-full space-y-0.5">
                                      <div className="flex h-auto w-full text-[10px]">
                                        <div className="flex flex-auto text-[#0000008a]">
                                          Assigned on:{" "}
                                          {useFormattedDate(
                                            value?.completed_date ?? ""
                                          )}
                                        </div>
                                        <div className={"text-[#27A745]"}>
                                          Completed
                                        </div>
                                      </div>
                                      <div className="flex space-x-2">
                                        <button
                                          onClick={() => {
                                            setLoadingID(index);
                                            viewPersonalizeReportFunction(
                                              value
                                            );
                                          }}
                                          className={`flex h-auto w-full cursor-pointer justify-center rounded-[5px] py-2 text-[12px] xl:py-1.5 xl:text-[10px] 2xl:text-[12px] ${
                                            selected?.session_id ==
                                            value.session_id
                                              ? "border border-[#F68D1E] bg-[#F68D1E] text-[#EEF8FB]"
                                              : "border border-[#F68D1E] text-[#F68D1E]"
                                          }`}
                                        >
                                          {loading && loadingID == index
                                            ? "Please Wait"
                                            : selected?.session_id ==
                                              value.session_id
                                            ? "Viewed"
                                            : "Personalize Report"}
                                        </button>
                                        <button
                                          onClick={() =>
                                            // SelectionFunction(value)
                                            NavigateFunction(value)
                                          }
                                          className={`flex h-auto w-full cursor-pointer justify-center rounded-[5px] py-2 text-[12px] xl:py-1.5 xl:text-[10px] 2xl:text-[12px] ${
                                            selected?.session_id ==
                                            value.session_id
                                              ? "border border-[#F68D1E] bg-[#F68D1E] text-[#EEF8FB]"
                                              : "border border-[#F68D1E] text-[#F68D1E]"
                                          }`}
                                        >
                                          {selected?.session_id ==
                                          value.session_id
                                            ? "Viewed"
                                            : "View Report"}
                                        </button>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                        </>
                      ))}

                    {loading && (
                      <div className="h-full w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] rounded-[10px] justify-center items-center">
                        <div role="status">
                          <svg
                            aria-hidden="true"
                            className="w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-[#597bd1]"
                            viewBox="0 0 100 101"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <path
                              d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                              fill="currentColor"
                            />
                            <path
                              d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                              fill="currentFill"
                            />
                          </svg>
                          <span className="sr-only">Loading...</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                {/* <hr className="mx-[3.5rem] h-0 text-[#131f4946] xl:mx-[2rem] 2xl:mx-[3.5rem]" />
                <div className="flex h-[5rem] w-full items-center justify-end px-[3.5rem] xl:h-[3rem] xl:px-[2rem] 2xl:h-[5rem] 2xl:px-[3.5rem]">
                  <button
                    onClick={() => NavigateFunction()}
                    className="flex h-auto w-[10rem] cursor-pointer items-center justify-center gap-2 rounded-[5px] bg-[#F68D1E] py-1 text-[18px] text-[#FFFFFF] xl:w-[8rem] xl:text-[14px] 2xl:w-[10rem] 2xl:text-[18px]"
                  >
                    Next <img src="./rightarrow.svg" alt="RightArrow" />
                  </button>
                </div> */}
              </div>
            </div>
          </div>
        </div>
        <ViewReportModel
          reportModelView={reportModelView}
          setReportModelView={setReportModelView}
          selected={selected}
          setSelected={setSelected}
          viewModel={viewModel}
          scenarioName={scenarioName}
        />
      </div>
    </div>
  );
};

export default ViewReport;
