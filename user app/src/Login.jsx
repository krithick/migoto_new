// Importing necessary libraries and components
import React from "react";
import LoginValidation from "./components/LoginValidation"; // Component for validating login inputs

// Main Login component
const Login = () => {
  const filepath = "https://meta.novactech.in/migoto-ai";
  return (
    <div className="absolute inset-0 backdrop-blur-[68px]">
      {/* Main container with grid layout */}
      <div className="h-screen w-screen relative grid grid-cols-4 place-content-evenly space-x-[5rem] px-[5rem]">
        {/* Migoto Container */}
        <div className="col-span-3 h-[85vh] w-auto bg-[#ffffff80] rounded-[30px] inset-shadow-sm inset-shadow-[#ffffff80] px-[5rem] py-[3.5rem] xl:px-[3rem] xl:py-[2.5rem] 2xl:px-[4rem] 2xl:py-[3rem]">
          {/* Header section with logo and description */}
          <div className="h-[15%] w-auto space-y-0">
            <img
              src={`${filepath}/MigotoLogo.png`}
              alt="Migoto Logo"
              loading="lazy"
              className="h-auto w-auto xl:w-[12rem] 2xl:w-[16rem] object-cover"
            />
            <div className="text-[20px] xl:text-[14px] 2xl:text-[20px] text-[#131F49]">
              Enhance your skills in a dynamic, interactive environment tailored
              to your learning needs.
            </div>
          </div>

          {/* Content section with image and feature list */}
          <div className="h-[85%] w-auto flex space-x-[5px] xl:space-x-[2.5rem]">
            {/* Left section with login image */}
            <div className="w-auto h-full flex justify-start items-end">
              <img
                src={`${filepath}/LoginImage.png`}
                loading="lazy"
                alt="Login Image"
                className="h-auto w-[33rem] xl:h-[20rem] xl:w-[25rem] 2xl:h-[33.5rem] 2xl:w-[40rem] object-contain xl:object-fill 2xl:object-fill"
              />
            </div>

            {/* Right section with feature list */}
            <div className="w-auto h-full flex justify-start items-end">
              <div className="grid space-y-[30px] xl:space-y-[12px] 2xl:space-y-[40px]">
                {/* Feature: AI Driven Scenario-Based Training */}
                <div className="flex space-x-[20px] items-center">
                  <img
                    src={`${filepath}/Login_AI.svg`}
                    loading="lazy"
                    alt="Login ai"
                    className="h-auto w-auto xl:w-[26px] 2xl:w-[28px] bg-[#131f496b] p-1.5 border-[#131F4926] border-rounded rounded"
                  />
                  <p className="text-[18px] xl:text-[12px] 2xl:text-[16px] text-[#131F49]">
                    AI Driven Scenario-Based Training
                  </p>
                </div>

                {/* Feature: Role Based Access */}
                <div className="flex space-x-[20px] items-center">
                  <img
                    src={`${filepath}/Login_role.svg`}
                    loading="lazy"
                    alt="Login role"
                    className="h-auto w-auto xl:w-[26px] 2xl:w-[28px] bg-[#131f496b] p-1.5 border-[#131F4926] border-rounded rounded"
                  />
                  <p className="text-[18px] xl:text-[12px] 2xl:text-[16px] text-[#131F49]">
                    Role Based Access
                  </p>
                </div>

                {/* Feature: Real-Time Performance Analytics and Feedback */}
                <div className="flex space-x-[20px] items-center">
                  <img
                    src={`${filepath}/Login_real.svg`}
                    alt="Login real"
                    loading="lazy"
                    className="h-auto w-auto xl:w-[26px] 2xl:w-[28px] bg-[#131f496b] p-1.5 border-[#131F4926] border-rounded rounded"
                  />
                  <p className="text-[18px] xl:text-[12px] 2xl:text-[16px] text-[#131F49]">
                    Real-Time Performance Analytics and Feedback
                  </p>
                </div>

                {/* Feature: Adaptive Learning */}
                <div className="flex space-x-[20px] items-center">
                  <img
                    src={`${filepath}/Login_adaptive.svg`}
                    loading="lazy"
                    alt="Login adaptive"
                    className="h-auto w-auto xl:w-[26px] 2xl:w-[28px] bg-[#131f496b] p-1.5 border-[#131F4926] border-rounded rounded"
                  />
                  <p className="text-[18px] xl:text-[12px] 2xl:text-[16px] text-[#131F49]">
                    Adaptive Learning
                  </p>
                </div>

                {/* Feature: VR Driven Realistic Simulations */}
                <div className="flex space-x-[20px] items-center">
                  <img
                    src={`${filepath}/Login_vr.svg`}
                    loading="lazy"
                    alt="Login vr"
                    className="h-auto w-auto xl:w-[26px] 2xl:w-[28px] bg-[#131f496b] p-1.5 border-[#131F4926] border-rounded rounded"
                  />
                  <p className="text-[18px] xl:text-[12px] 2xl:text-[16px] text-[#131F49]">
                    VR Driven Realistic Simulations
                  </p>
                </div>

                {/* Feature: Compliance Tracking and Reporting */}
                <div className="flex space-x-[20px] items-center">
                  <img
                    src={`${filepath}/Login_vr.svg`}
                    loading="lazy"
                    alt="Login compliance"
                    className="h-auto w-auto xl:w-[26px] 2xl:w-[28px] bg-[#131f496b] p-1.5 border-[#131F4926] border-rounded rounded"
                  />
                  <p className="text-[18px] xl:text-[12px] 2xl:text-[16px] text-[#131F49]">
                    Compliance Tracking and Reporting
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Login Container */}
        <div className="col-span-1 h-[85vh] w-auto bg-[#192348] rounded-[30px] py-[5rem] xl:py-[3rem] 2xl:py-[5rem] space-y-[4rem] xl:space-y-[2.2rem] 2xl:space-y-[4rem]">
          {/* Logo section */}
          <div className="flex justify-center">
            <img
              src={`${filepath}/ImmerzLogo.png`}
              loading="lazy"
              alt="Immerz Logo"
              className="h-auto w-auto xl:h-[2.2rem] 2xl:h-[3rem] object-contain"
            />
          </div>

          {/* Login title */}
          <div className="flex justify-center text-[#EBF7FA] text-[22px] xl:text-[16px] 2xl:text-[22px]">
            <p>Login</p>
          </div>

          {/* Welcome message */}
          <div className="flex justify-center text-center">
            <div>
              <p className="text-[20px] xl:text-[14px] 2xl:text-[22px] text-[#EBF7FA]">
                Welcome back
              </p>
              <span className="text-[#ffffff83] text-[14px] xl:text-[10px] 2xl:text-[14px]">
                Sign in by entering your account here
              </span>
            </div>
          </div>

          {/* Login validation form */}
          <div className="h-[20rem] xl:h-[14rem] 2xl:h-[20rem] flex justify-center items-end">
            <LoginValidation filepath={filepath} />
          </div>
        </div>
      </div>
    </div>
  );
};

// Exporting the Login component as default
export default Login;
