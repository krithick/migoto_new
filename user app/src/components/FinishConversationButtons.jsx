import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import instance from "../service";
import toast from "react-hot-toast";

const FinishConversationButtons = ({
  audioRef,
  setMic,
  setAudioReload,
  mode,
  setConversationHistory,
  setFinishButton,
  disable,
  setSessionId,
}) => {
  const [view, setView] = useState(false);
  const [loading, setLoading] = useState(false);
  const [scenario, setScenario] = useState(null);
  let navigate = useNavigate();
  useEffect(() => {
    if (localStorage.getItem("migoto-scenario")) {
      setScenario(JSON.parse(localStorage.getItem("migoto-scenario")));
    }
  }, []);

  const CallApiforComplete = () => {
    if (mode != "Assess Mode") {
      if (audioRef.current) {
        audioRef.current.pause();
        console.log("Audio stopped");
      }
      setAudioReload(false);
    }
    setLoading(true);
    const headers = {
      "Content-Type": "multipart/form-data",
      Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
    };

    instance
      .put(
        `/scenario-assignments/me/scenario/${scenario?.id}/mode/${
          mode == "Try Mode" ? "try_mode" : "learn_mode"
        }/complete`,
        null,
        { headers }
      )
      .then((responce) => {
        setLoading(false);
        setView(true);
      })
      .catch((error) => {
        setLoading(false);
        setView(false);
        console.log("error: ", error);
        toast.error("try again");
      });
  };

  const NavigateFunction = () => {
    localStorage.removeItem("migoto-avatar");
    localStorage.removeItem("migoto-language");
    localStorage.removeItem("migoto-voice");
    localStorage.removeItem("migoto-environment");
    localStorage.removeItem("migoto-sessionId");
    localStorage.setItem("migoto-url", "/assigned-mode");
    navigate("/assigned-mode", { replace: true });
  };

  const PreviousNavigation = () => {
    if (mode == "Assess Mode") {
      localStorage.removeItem("migoto-sessionId");
      localStorage.setItem("migoto-url", "/conversation");
      navigate("/conversation", { replace: true });
    } else {
      setMic(false);
      setFinishButton(false);
      localStorage.removeItem("migoto-sessionId");
      setConversationHistory([]);
      setView(false);
      // setSessionId(null);
    }
  };

  return (
    <>
      {/* {loading ? (
        <></>
      ) : (
        <button
          disabled={!disable}
          onClick={() => CallApiforComplete()}
          className={`h-auto w-[10rem] xl:w-[12rem] 2xl:w-[13rem] bg-[#F68D1E] flex justify-center items-center gap-2 py-1.5 text-[#FFFFFF] text-[18px] xl:text-[14px] 2xl:text-[16px] rounded-[5px] ${
            disable
              ? "bg-[#F68D1E] cursor-pointer"
              : "bg-gray-300 cursor-default"
          }`}
        >
          {`${
            mode == "Evaluate Mode" || mode == "learn"
              ? "Finish"
              : "Finish Conversation"
          }`}
          <img src="./rightarrow.svg" alt="RightArrow" />
        </button>
      )} */}

      {loading ? (
        <div className="flex gap-4">
          {/* Finish Conversation Button */}
          <button
            disabled={!disable}
            className={`h-auto w-[10rem] xl:w-[12rem] 2xl:w-[13rem] bg-[#F68D1E] flex justify-center items-center gap-2 py-1.5 text-[#FFFFFF] text-[18px] xl:text-[14px] 2xl:text-[16px] rounded-[5px] ${
              disable
                ? "bg-[#F68D1E] cursor-pointer"
                : "bg-gray-300 cursor-default"
            }`}
          >
            {/* <button className="bg-[#F68D1E] w-full h-[2.8rem] xl:h-[2.2rem] 2xl:h-[3rem] text-white text-[20px] xl:text-[16px] 2xl:text-[18px] flex justify-center items-center font-medium rounded-[10px] cursor-pointer"> */}
            <div role="status">
              <svg
                aria-hidden="true"
                className="w-6 h-6 text-gray-200 animate-spin dark:text-gray-600 fill-[#597bd1]"
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
            {/* </button> */}
          </button>
        </div>
      ) : (
        <div className="flex gap-4">
          {/* Finish Conversation Button */}
          <button
            disabled={!disable}
            onClick={() => CallApiforComplete()}
            className={`h-auto w-[10rem] xl:w-[12rem] 2xl:w-[13rem] bg-[#F68D1E] flex justify-center items-center gap-2 py-1.5 text-[#FFFFFF] text-[18px] xl:text-[14px] 2xl:text-[16px] rounded-[5px] ${
              disable
                ? "bg-[#F68D1E] cursor-pointer"
                : "bg-gray-300 cursor-default"
            }`}
          >
            {`${
              mode == "Evaluate Mode" || mode == "learn"
                ? "Finish"
                : "Finish Conversation"
            }`}
            <img src="./rightarrow.svg" alt="RightArrow" loading="lazy" />
          </button>
        </div>
      )}

      {view && (
        <div className="absolute inset-0 h-[35.5rem] xl:h-[35.5rem] 2xl:h-[56.5rem]  w-screen mt-[58px] xl:mt-[44px] 2xl:mt-[58px]  z-20 flex justify-center items-center bg-[#00000065] backdrop-blur-[10px]">
          <div className="h-[16rem] w-[34rem] bg-[#FFFFFF] inset-shadow-[6px] rounded-[10px]">
            <div className="h-[3rem] w-full px-5 flex items-center">
              <div className="text-[#131F49] text-[16px] font-medium flex flex-auto">
                Congratulations!
              </div>
              <div>
                <img
                  src="./close.svg"
                  loading="lazy"
                  alt="close"
                  className="cursor-pointer"
                  onClick={() => {
                    if (mode != "Assess Mode") {
                      setMic(false);
                      setView(false);
                    } else {
                      setView(false);
                    }
                  }}
                />
              </div>
            </div>
            <hr />
            <div className="h-[9.5rem] w-full flex px-10 items-center text-[#131F49] text-[16px] font-normal">
              {`You have completed ${
                mode == "Assess Mode"
                  ? "Assess Mode"
                  : `${mode == "learn" ? "Learn Mode" : "Try Mode"}`
              }`}
            </div>
            <div className="h-[3rem] w-full flex justify-between px-3 py-2">
              <button
                onClick={() => PreviousNavigation()}
                className="h-auto w-[10rem] xl:w-[12rem] 2xl:w-[12rem] border border-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#F68D1E] text-[18px] xl:text-[14px] 2xl:text-[14px] rounded-[5px] cursor-pointer"
              >
                <img src="./leftarrow.svg" alt="LeftArrow" loading="lazy" />
                {`${mode == "learn" ? "Back" : "Restart Conversation"}`}
                {/* Restart Conversation */}
              </button>
              <button
                onClick={() => NavigateFunction()}
                className="h-auto w-[10rem] xl:w-[12rem] 2xl:w-[12rem] bg-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#FFFFFF] text-[18px] xl:text-[14px] 2xl:text-[14px] rounded-[5px] cursor-pointer"
              >
                Return{" "}
                <img src="./rightarrow.svg" alt="RightArrow" loading="lazy" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FinishConversationButtons;
