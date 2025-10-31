import React, { useEffect, useState } from "react";
import { IoReload } from "react-icons/io5";
import { useNavigate } from "react-router";
import Logout from "./Logout";
import { MdOutlineLogout } from "react-icons/md";

const HeaderMenu = ({ audioRef, index, disable, reload, setReload }) => {
  let navigate = useNavigate();
  const [currentTab, setCurrentTab] = useState("home");
  const [userDetails, setUserDetails] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showLogoutConfirmationDialog, setShowLogoutConfirmationDialog] =
    useState(false);
  const NavigatePage = (props) => {
    setCurrentTab(props);
    // navigate(`/${props}`);
  };

  useEffect(() => {
    if (localStorage.getItem("migoto-user") != null) {
      const user = JSON.parse(localStorage.getItem("migoto-user"));
      setUserDetails(user);
    }
  }, []);
  return (
    <>
      <div className="h-[58px] xl:h-[44px] 2xl:h-[58px] w-screen bg-[#131F49] flex px-[4.5rem]">
        <div className="flex flex-auto items-center">
          <img
            src="./MigotoLogoWhite.png"
            loading="lazy"
            alt="Migoto White"
            className="h-auto w-[7rem] object-contain"
          />
        </div>
        <div className="h-full w-auto flex items-center space-x-[4rem] xl:space-x-[2rem] 2xl:space-x-[4rem] text-[14px] xl:text-[12px] 2xl:text-[14px]">
          {/* <div
          onClick={() => NavigatePage("home")}
          className={`cursor-pointer ${
            currentTab == "home" ? "text-[#F68D1E]" : "text-[#E9F5F9]"
          }`}
        >
          Home
        </div> */}
          <div
            onClick={() => {
              if (disable)
                navigate(localStorage.getItem("migoto-url"), { replace: true });
            }}
            className={` ${
              !disable
                ? "text-[#e9f5f977] cursor-default"
                : index == "1"
                ? "text-[#F68D1E] cursor-pointer"
                : "text-[#E9F5F9] cursor-pointer"
            }`}
          >
            Assigned Courses
          </div>
          {/* <div
          onClick={() => NavigatePage("completed-course")}
          className={`cursor-pointer ${
            currentTab == "completed-course"
              ? "text-[#F68D1E]"
              : "text-[#E9F5F9]"
          }`}
        >
          Completed Courses
        </div> */}
          <div
            onClick={() => {
              if (disable) navigate("/view-report", { replace: true });
            }}
            className={` ${
              !disable
                ? "text-[#e9f5f977] cursor-default"
                : index == "2"
                ? "text-[#F68D1E] cursor-pointer"
                : "text-[#E9F5F9] cursor-pointer"
            }`}
          >
            View Reports
          </div>
          <div className="flex items-center space-x-[10px] relative ">
            {/* user details */}
            <div
              onClick={() => setShowUserMenu(!showUserMenu)}
              className={`flex items-center space-x-[10px] cursor-pointer transition-all duration-700 ease-in-out
            ${currentTab == "assign" ? "text-[#F68D1E]" : "text-[#E9F5F9]"}`}
            >
              <img src="./user.svg" alt="user" loading="lazy" />
              <span>{userDetails && userDetails.username}</span>
              <img
                src="./downarrow.svg"
                loading="lazy"
                alt="downarrow"
                className={`${!showUserMenu ? "rotate-0" : "-rotate-180"}`}
              />
            </div>
            {showUserMenu && (
              <div className="absolute right-16 top-[100%] mt-3.5 w-40 bg-[#131F49] hover:bg-[#131f49c9] hover:rounded text-[#DEF0F7] rounded  shadow z-50 ">
                <div
                  className="px-4 py-2 cursor-pointer flex justify-between items-center"
                  onClick={() => {
                    if (audioRef?.current) {
                      audioRef?.current.pause();
                      // audioRef.current.currentTime = 0;
                    }
                    setShowLogoutConfirmationDialog(
                      !showLogoutConfirmationDialog
                    );
                    setShowUserMenu(!showUserMenu);
                  }}
                >
                  Logout
                  <MdOutlineLogout size={20} />
                </div>
              </div>
            )}
            <div className="w-[1px] h-auto py-4 bg-white"></div>
            <div>
              <button
                onClick={() => setReload(!reload)}
                className="flex items-center justify-center px-3.5 py-0.5 rounded bg-[#F68D1E] text-[#FFFFFF] text-[10px] gap-x-1 cursor-pointer"
              >
                Sync
                <IoReload />
              </button>
            </div>
          </div>
        </div>
      </div>
      {showLogoutConfirmationDialog && (
        <Logout
          audioRef={audioRef}
          showLogoutConfirmationDialog={showLogoutConfirmationDialog}
          setShowLogoutConfirmationDialog={setShowLogoutConfirmationDialog}
        />
      )}
    </>
  );
};

export default HeaderMenu;
