import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import instance from "./service"; // axios instance with baseURL and token set
import HeaderMenu from "./components/HeaderMenu";
import AssignSideMenu from "./components/AssignSideMenu";
import FinishConversationButtons from "./components/FinishConversationButtons";
import { DynamicDataBinding } from "./components/DynamicDataBinding";

const PersonalizedReport = () => {
  const navigate = useNavigate();
  const [userReport, setUserReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reload, setReload] = useState(false);
  const [close, setClose] = useState(false);

  const generateAndFetchReport = () => {
    const sessionID = localStorage.getItem("migoto-sessionId");

    if (!sessionID) {
      console.error("Session ID not found.");
      navigate(-1);
      return;
    }

    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("migoto-token")}`,
    };

    // Call POST API to generate the report
    instance
      .post(`/chat/evaluate/${sessionID}`, {}, { headers })
      .then((response) => {
        setUserReport(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error generating report:", error);
        setLoading(false);
      });
  };

  useEffect(() => {
    generateAndFetchReport();
  }, []);

  return (
    <div className="absolute inset-0 backdrop-blur-[68px]">
      <div className="h-screen w-screen relative">
        <HeaderMenu
          index={"1"}
          reload={reload}
          disable={true}
          setReload={setReload}
        />
        <div className="h-[35.5rem] xl:h-[35.5rem] 2xl:h-[54rem] w-screen flex items-center">
          <div className="h-full w-screen place-content-center px-[10rem] xl:px-[7.5rem] 2xl:px-[10rem] pb-[5rem]">
            <div className="h-[50px] xl:h-[40px] 2xl:h-[50px] flex items-center text-[#000000] text-[16px] xl:text-[14px] 2xl:text-[16px] font-medium">
              Assigned Courses
            </div>
            <div className="h-full w-full bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px] flex">
              <div
                className={`transition-all duration-700 ease-in-out animate-fade-left animate-ease-linear h-full w-[45rem] ${
                  close
                    ? "xl:w-[70rem] 2xl:w-[100rem]"
                    : "xl:w-[55.5rem] 2xl:w-[80rem]"
                }`}
              >
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <div className="flex flex-auto justify-start">
                    <div className="flex flex-auto justify-start">
                      <div className="flex flex-auto items-center space-x-[10px]">
                        <span className="text-[16px] xl:text-[14px] 2xl:text-[16px] text-[#131F49]">
                          Personalized Report
                        </span>
                      </div>
                      {close && (
                        <div className="has-tooltip">
                          <span className="tooltip p-1 mt-6 text-[12px] rounded bg-[#131f4928] border border-[#FFFFFF]">
                            Progress Bar
                          </span>
                          <img
                            loading="lazy"
                            onClick={() => setClose(false)}
                            src="./menu.svg"
                            alt="menu"
                            className="bg-[#131f4928] border border-[#FFFFFF] p-1.5 cursor-pointer"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[40.8rem] xl:h-[24rem] 2xl:h-[39rem] w-full px-[3.5rem] py-[15px] xl:py-[10px] 2xl:py-[15px]">
                  {!loading ? (
                    <div className="h-full w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] bg-[#FFFFFF8F] rounded-[10px]">
                      <div
                        className={`h-full rounded-[10px] pr-5 pl-6 py-5 transition-all duration-1000 ease-in-out animate-fade-left animate-ease-linear ${
                          close
                            ? "w-[48.5rem] xl:w-[58rem] 2xl:w-[90rem]"
                            : "w-[25rem] xl:w-[44rem] 2xl:w-[80rem]"
                        }`}
                      >
                        <div
                          className="flex flex-col place-content-start px-3 py-0 space-y-3 xl:space-y-1 2xl:space-y-3 h-[94%] w-auto  overflow-y-auto  [&::-webkit-scrollbar]:w-1
                                [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:rounded-full
                                [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:bg-gray-400"
                        >
                          {userReport && (
                            <DynamicDataBinding data={userReport?.evaluation} />
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="h-full w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] bg-[#FFFFFF8F] rounded-[10px] justify-center items-center">
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
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-end items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <FinishConversationButtons
                    mode={"Assess Mode"}
                    disable={true}
                  />
                </div>
              </div>
              <div
                className={`transition-all duration-700 ease-in h-full ${
                  close ? "w-0" : "xl:w-[15rem] 2xl:w-[20rem]"
                } bg-[#FFFFFF8F] inset-shadow-sm inset-shadow-[#ffffff] rounded-r-[10px] cursor-default`}
              >
                <AssignSideMenu index={11} close={close} setClose={setClose} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PersonalizedReport;
