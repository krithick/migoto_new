import React from "react";
import { useNavigate } from "react-router";

const Logout = ({
  audioRef,
  showUserMenu,
  setShowUserMenu,
  setShowLogoutConfirmationDialog,
  showLogoutConfirmationDialog,
}) => {
  let navigate = useNavigate();
  const Logout = () => {
    if (audioRef?.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    localStorage.clear();
    navigate("/", { replace: true });
  };
  return (
    <div className="absolute inset-0 h-[35.5rem] xl:h-[35.5rem] 2xl:h-[56.5rem]  w-screen mt-[58px] xl:mt-[44px] 2xl:mt-[58px]  z-20 flex justify-center items-center bg-[#00000065] backdrop-blur-[10px]">
      <div className="h-[16rem] w-[40rem] bg-[#FFFFFF] inset-shadow-[6px] rounded-[10px]">
        <div className="h-full w-full p-5 flex flex-col">
          <div className="h-[20%] w-full flex gap-2">
            <div className="h-full w-auto flex flex-auto items-center pl-5 gap-5 font-bold text-[#131F49] text-[18px]">
              Logout
            </div>
          </div>
          <hr className="bg-[#3E4580] h-0.5" />
          <div className="h-[80%] w-full flex flex-col">
            <span className="h-[75%] flex flex-auto justify-start items-center text-[#131F49] text-[16px]">
              Are you sure you want to logout?
            </span>
            <div className="h-[25%] w-full flex justify-end items-center px-3 gap-5">
              <button
                onClick={() => {
                  if (audioRef?.current) {
                    audioRef.current.play();
                    // audioRef.current.currentTime = 0;
                  }
                  setShowLogoutConfirmationDialog(
                    !showLogoutConfirmationDialog
                  );
                  setShowUserMenu(!showUserMenu);
                }}
                className="border border-[#F68D1E] h-10 w-40 rounded-md text-[#F68D1E] cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => Logout()}
                className="h-10 w-40 bg-[#F68D1E] hover:bg-[#f68e1ebd] text-[#FFFFFF] rounded-md cursor-pointer"
              >
                Yes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Logout;
