const PersonaInfo = ({
  personaInfo,
  personaInfoDetails,
  setPersonaInfo,
  setPersonaInfoDetails,
}) => {
  return (
    <>
      {personaInfo && (
        <div className="absolute inset-0 h-[35.5rem] xl:h-[35.5rem] 2xl:h-[56.5rem]  w-screen mt-[58px] xl:mt-[44px] 2xl:mt-[58px]  z-20 flex justify-center items-center bg-[#00000065] backdrop-blur-[10px]">
          <div className="h-[25rem] w-[50rem] bg-[#FFFFFF] inset-shadow-[6px] rounded-[10px]">
            <div className="h-[2.5rem] w-full px-5 flex items-center">
              <div className="text-[#131F49] text-[16px] font-medium flex flex-auto">
                Persona Selection
              </div>
              <div>
                <img
                  src="./close.svg"
                  loading="lazy"
                  alt="close"
                  className="cursor-pointer"
                  onClick={() => {
                    setPersonaInfo(!personaInfo);
                    setPersonaInfoDetails(null);
                  }}
                />
              </div>
            </div>
            <div className="h-[22.5rem] w-full flex">
              <div className="h-full w-[18rem] px-2.5 space-y-2">
                <div className="h-[85%] w-full flex items-end">
                  <img
                    loading="lazy"
                    src={personaInfoDetails.thumbnail_url}
                    alt={personaInfoDetails.name}
                    className="h-full w-full object-contain bg-[#BFBFBF3B] rounded-[5px] border border-[#BFBFBF3B]"
                  />
                </div>
                <div>
                  <button className="flex justify-center items-center w-full h-full bg-[#F68D1E] border border-[#F68D1E] text-[#EEF8FB] text-[12px] py-1.5 rounded-[5px]">
                    Select
                  </button>
                </div>
              </div>
              <div className="h-full w-[32rem] px-2.5 space-y-2">
                <div className="text-[#000000] text-[16px] font-[600]">
                  {personaInfoDetails.persona_id[0]?.name}
                </div>
                <div className="text-[#000000d2] font-medium text-[12px]">
                  Age: {personaInfoDetails.persona_id[0]?.age}
                </div>
                <div className="text-[#000000d2] font-medium text-[12px]">
                  Profession: {personaInfoDetails.persona_id[0].persona_type}
                </div>
                <div className="h-[16.3rem] w-full p-2 bg-[#7070701C] border border-[#7070701C] rounded-[10px]">
                  <div className="h-full w-full text-[#000000bb] leading-5 text-[12px] overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                    <div>Description</div>
                    <div>
                      {personaInfoDetails.persona_id[0].persona_details}
                    </div>
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

export default PersonaInfo;
