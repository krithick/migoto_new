// Importing necessary libraries and components
import React, { useState } from "react";
import { useNavigate } from "react-router"; // React Router for navigation
import instance from "../service"; // Axios instance for API calls

// LoginValidation component for handling user login
const LoginValidation = ({ filepath }) => {
  let navigate = useNavigate(); // React Router's navigation hook
  const [error, setError] = useState(false); // State to track login errors
  const [loading, setLoading] = useState(false); // State to track login errors
  const [showPassword, setShowPassword] = useState(false); // State to toggle password visibility
  const [username, setUsername] = useState(null); // State to store the username
  const [password, setPassword] = useState(null); // State to store the password

  // Function to handle user login
  function HandleLoginUser(e) {
    e.preventDefault(); // Prevent default form submission behavior
    localStorage.clear(); // Clear local storage
    setError(false); // Reset error state
    setLoading(true); // Set loading state to true

    // Hardcoded credentials for testing (replace with dynamic inputs)
    const credentials = {
      // email: "user1@example.com",
      // password: "Password123!",
      email: username, // Use dynamic username input
      password: password, // Use dynamic password input
    };

    // API call to authenticate the user
    instance
      .post("/auth/login", credentials)
      .then((response) => {
        // Fetch and load the user's token
        const headers = {
          "Content-Type": "application/json",
          Authorization: `Bearer ` + response.data.access_token,
        };

        // API call to fetch user details
        instance
          .get("/auth/users/me", { headers })
          .then((res) => {
            if (res.data.role === "user") {
              setLoading(false); // Reset loading state
              // Navigate to the assigned courses page if the user role is valid
              navigate("/assigned-course", { replace: true });

              // Save token and user details to local storage
              localStorage.setItem("migoto-token", response.data.access_token);
              localStorage.setItem("migoto-user", JSON.stringify(res.data));
              localStorage.setItem("migoto-url", "/assigned-course");
            }
          })
          .catch((err) => {
            setLoading(false); // Reset loading state
            console.log("Login Error : ", err); // Log any errors during user details fetch
          });
      })
      .catch((error) => {
        console.log("Login Error : ", error); // Log any errors during login
        setLoading(false); // Reset loading state
        setError(true); // Set error state to true if login fails
      });
  }

  // JSX structure for rendering the login form
  return (
    <form
      className="space-y-5 xl:space-y-3 2xl:space-y-8"
      onSubmit={HandleLoginUser} // Handle form submission
    >
      {/* Error message for invalid credentials */}
      {error && (
        <div className="flex justify-center items-center gap-2">
          <img
            src={`${filepath}/LoginError.svg`}
            loading="lazy"
            alt="Login Error"
            className="h-auto w-auto xl:h-[16px] 2xl:h-[16px] object-contain"
          />
          <span className="text-[14px] xl:text-[10px] 2xl:text-[14px] text-[#FF3B3B]">
            Invalid Credentials
          </span>
        </div>
      )}

      {/* Input fields for username and password */}
      <div className="space-y-4 2xl:space-y-6 flex flex-col flex-auto items-center pb-5">
        {/* Username input */}
        <div
          className={`flex w-72 xl:w-[16rem] 2xl:w-[21rem] flex-col space-y-0 overflow-hidden rounded-md border ${
            error ? "border-[#FF3B3B]" : "border-[#CDCDCD]"
          } py-0.5`}
        >
          <span className="px-3 text-[10px] whitespace-nowrap text-[#9BB2EE]">
            Username
          </span>
          <input
            autoComplete="off"
            type="text"
            className="flex-1 px-3 py-0.5 text-[16px] xl:text-[14px] 2xl:text-[16px] text-white focus:outline-none"
            placeholder="Enter username"
            onChange={(e) => setUsername(e.target.value)} // Update username state
          />
        </div>

        {/* Password input */}
        <div>
          <div
            className={`relative flex w-72 xl:w-[16rem] 2xl:w-[21rem] flex-col space-y-0 overflow-hidden rounded-md border ${
              error ? "border-[#FF3B3B]" : "border-[#CDCDCD]"
            } py-0.5`}
          >
            <span className="px-3 text-[10px] whitespace-nowrap text-[#9BB2EE]">
              Password
            </span>
            <input
              autoComplete="off"
              type={showPassword ? "text" : "password"} // Toggle password visibility
              className="flex-1 bg-transparent px-3 py-0.5 pr-10 text-[16px] xl:text-[14px] 2xl:text-[16px] text-white focus:outline-none"
              placeholder="Enter password"
              onChange={(e) => setPassword(e.target.value)} // Update password state
            />
            <img
              src={`${filepath}/eye_close.svg`}
              loading="lazy"
              alt="eye icon"
              className="absolute right-3 bottom-1.5 h-5 w-5 cursor-pointer opacity-70 hover:opacity-100"
              onClick={() => setShowPassword(!showPassword)} // Toggle password visibility
            />
          </div>
          <span className="text-[#ffffff83] text-[12px] xl:text-[10px] 2xl:text-[12px]">
            Forgot Password?
          </span>
        </div>
      </div>

      {/* Login button */}
      <div>
        {!loading ? (
          <button
            type="submit"
            className="bg-[#F68D1E] w-full h-[2.8rem] xl:h-[2.2rem] 2xl:h-[3rem] text-white text-[20px] xl:text-[16px] 2xl:text-[18px] font-medium rounded-[10px] cursor-pointer"
          >
            Login
          </button>
        ) : (
          <button className="bg-[#F68D1E] w-full h-[2.8rem] xl:h-[2.2rem] 2xl:h-[3rem] text-white text-[20px] xl:text-[16px] 2xl:text-[18px] flex justify-center items-center font-medium rounded-[10px] cursor-pointer">
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
          </button>
        )}
      </div>
    </form>
  );
};

// Exporting the LoginValidation component
export default LoginValidation;
