import { useNavigate } from "react-router";

const NotFoundPageOnMobile = () => {
  // React Router's navigation hook
  let navigate = useNavigate();
  return (
    <div className="absolute inset-0 backdrop-blur-[68px]">
      <div className="h-screen w-screen  fixed px-[3rem] py-[3rem]">
        <div className="h-full w-full flex justify-center items-center bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px]">
          <div className="text-center">
            <img
              src="./notfound.svg"
              alt="notfound"
              className="h-[25rem] w-auto object-cover"
              loading="lazy"
            />
            {/* <h1 className="mb-4 text-6xl font-semibold text-red-500">404</h1>
          <p className="mb-4 text-lg text-gray-600">
            Oops! Looks like you're lost.
          </p>
          <div className="animate-bounce">
            <svg
              className="mx-auto h-16 w-16 text-green-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              ></path>
            </svg> */}
            {/* </div> */}
            <p className="mt-4 text-gray-600">
              Let's get you back{" "}
              <span
                onClick={() => navigate("/", { replace: true })}
                className="text-[#131F49] font-semibold cursor-pointer animate-pulse hover:animate-none"
              >
                Login
              </span>
              .
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPageOnMobile;
