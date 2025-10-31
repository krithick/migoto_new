const ScenarioInfo = ({
  scenarioInfo,
  scenarioInfoDetails,
  setScenarioInfo,
  setScenarioInfoDetails,
}) => {
  return (
    <>
      {scenarioInfo && (
        <div className="absolute inset-0 h-[35.5rem] xl:h-[35.5rem] 2xl:h-[56.5rem]  w-screen mt-[58px] xl:mt-[44px] 2xl:mt-[58px]  z-20 flex justify-center items-center bg-[#00000065] backdrop-blur-[10px]">
          <div className="h-[25rem] w-[50rem] bg-[#FFFFFF] inset-shadow-[6px] rounded-[10px]">
            <div className="h-[2.5rem] w-full px-5 flex items-center">
              <div className="text-[#131F49] text-[16px] font-medium flex flex-auto">
                Scenario Description
              </div>
              <div>
                <img
                  loading="lazy"
                  src="./close.svg"
                  alt="close"
                  className="cursor-pointer"
                  onClick={() => {
                    setScenarioInfo(!ScenarioInfo);
                    setScenarioInfoDetails(null);
                  }}
                />
              </div>
            </div>
            <div className="h-[22.5rem] w-full flex">
              <div className="h-full w-full px-10 space-y-2">
                <div className="text-[#000000] text-[16px] font-[600]">
                  {scenarioInfoDetails?.title}
                </div>
                <div className="text-[#000000d2] font-medium text-[12px]">
                  Status:{" "}
                  <span
                    className={`${
                      scenarioInfoDetails?.completed
                        ? "text-[#27A745]"
                        : "text-[#A4A029]"
                    }`}
                  >
                    {scenarioInfoDetails?.completed
                      ? "Completed"
                      : "Yet to Start"}
                  </span>
                </div>
                <div className="h-[16.3rem] w-full p-2 bg-[#7070701C] border border-[#7070701C] rounded-[10px]">
                  <div className="h-full w-full text-[#000000bb] leading-5 text-[12px] overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                    <div className="font-semibold">Description</div>
                    <div>{scenarioInfoDetails?.description}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ScenarioInfo;
