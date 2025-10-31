import React, { useState } from "react";
import AssignSideMenu from "./components/AssignSideMenu";
import HeaderMenu from "./components/HeaderMenu";
import { useNavigate } from "react-router";
import PersonaInfo from "./components/PersonaInfo";
import toast from "react-hot-toast";

const AssignedPersona = () => {
  const PersonaDetails = [
    {
      url: "/coursedummy.png",
      title: "Ganapathy",
      age: "24",
      profession: "Full stack developer",
      description:
        "Lorem ipsum dolor, sit amet consectetur adipisicing elit. Nulla molestiae magnam, nobis ratione laboriosam tempora repudiandae illum inventore sint, culpa ducimus voluptatibus totam. Iure eaque voluptates necessitatibus, eum ea accusantium! Lorem ipsum dolor sit amet consectetur adipisicing elit. Amet ut magni cumque hic ipsam consequuntur, asperiores alias, enim illo possimus dolore quidem sed obcaecati tenetur aperiam? Fugiat provident totam earum! Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque itaque ipsum iste inventore. Quo, nobis laudantium atque placeat eos, alias sed optio eveniet itaque in mollitia ipsum quia, maxime necessitatibus?",
      assignDate: "04.04.25",
      status: "View more...",
    },
    {
      url: "/coursedummy.png",
      title: "Sunil",
      age: "26",
      profession: "Front end developer",
      description:
        "Sunil is a detail-driven UI/UX designer who crafts intuitive, inclusive digital experiences with a minimalist touch.",
      assignDate: "04.04.25",
      status: "View more...",
    },
    {
      url: "/coursedummy.png",
      title: "Gowtham",
      age: "28",
      profession: "Back end developer",
      description:
        "Gowtham is a detail-driven UI/UX designer who crafts intuitive, inclusive digital experiences with a minimalist touch.",
      assignDate: "04.04.25",
      status: "View more...",
    },
  ];

  const [selected, setSelected] = useState(null);
  const [personaInfo, setPersonaInfo] = useState(false);
  const [personaInfoDetails, setPersonaInfoDetails] = useState(null);
  let navigate = useNavigate();

  const SelectionFunction = (props) => {
    if (selected == null) {
      setSelected(props);
    } else {
      if (selected.title == props.title) {
        setSelected(null);
      } else {
        setSelected(props);
      }
    }
  };

  const NavigateFunction = () => {
    if (selected != null) {
      localStorage.setItem("migoto-persona", JSON.stringify(selected));
      navigate("/assigned-avatar");
    } else {
      toast.error("Please select persona");
    }
  };

  return (
    <div className="absolute inset-0 backdrop-blur-[68px]">
      <div className="h-screen w-screen relative">
        <HeaderMenu />
        <div className="h-[35.5rem] xl:h-[35.5rem] 2xl:h-[56rem] w-screen flex items-center">
          <div className="h-full w-screen place-content-center px-[10rem] xl:px-[7.5rem] 2xl:px-[10rem] pb-[5rem]">
            <div className="h-[50px] xl:h-[40px] 2xl:h-[50px] flex items-center text-[#000000] text-[16px] xl:text-[14px] 2xl:text-[16px] font-medium">
              Assigned Courses
            </div>
            <div className="h-full w-full bg-[#ffffff80] rounded-l-[30px] rounded-r-[10px] flex">
              <div className="h-full w-[80rem]">
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <div className="flex flex-auto justify-start">
                    <div>
                      <div className="flex items-center space-x-[10px]">
                        <img
                          src="./scenario_current.svg"
                          alt="scenario"
                          loading="lazy"
                          className="h-auto w-auto xl:h-[14px] 2xl:h-auto object-contain"
                        />
                        <span className="text-[16px] xl:text-[14px] 2xl:text-[16px] text-[#131F49]">
                          Persona Selection
                        </span>
                      </div>
                      <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#131F49]">
                        Assigned Persona: 4
                      </div>
                    </div>
                  </div>
                  <div className="relative w-[247px] xl:w-[175px] 2xl:w-[247px]">
                    <input
                      type="text"
                      placeholder="Search"
                      className="w-full rounded-[30px] text-[10px] 2xl:text-[12px] text-[#000000] bg-[#C7DFF0] py-2 pr-4 pl-10 focus:outline-none"
                    />
                    <div className="absolute top-1/2 left-3 -translate-y-1/2 text-gray-400">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-[12px] xl:h-[14px] 2xl:h-[14px] w-5"
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
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[40.8rem] xl:h-[24rem] 2xl:h-[40.8rem] w-full pl-[3.5rem] xl:pl-[2rem] 2xl:pl-[3.5rem] pr-[22px] xl:pr-[14px] 2xl:pr-[22px] py-[15px] xl:py-[10px] 2xl:py-[15px]">
                  <div className="h-full w-full flex flex-wrap gap-x-[5rem] xl:gap-x-[2.5rem] 2xl:gap-x-[5rem] space-y-[36px] overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                    {PersonaDetails.map((value, index) => (
                      <div
                        key={index}
                        className="h-[18rem] xl:h-[20rem] 2xl:h-[26rem] w-[21rem] xl:w-[15rem] 2xl:w-[21rem] p-[5px] bg-[#FFFFFF] rounded-[10px]"
                      >
                        <div className="h-full w-full">
                          <img
                            src={value.url}
                            loading="lazy"
                            alt={value.title + index}
                            className="h-[55%] xl:h-[50%] 2xl:h-[55%] w-full object-contain bg-[#E9E9E9] rounded-t-[10px]"
                          />
                          <div className="h-[45%] w-full">
                            <div className="h-[4.4rem] xl:h-[6.3rem] 2xl:h-[7.5rem] w-full space-y-0.5">
                              <div className="text-[#000000] text-[16px] xl:text-[12px] 2xl:text-[16px] font-[600]">
                                {value.title}
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#000000ce] font-normal">
                                Age: 28
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#000000ce] font-normal">
                                Profession: UI/UX Designer
                              </div>
                              <div className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#0000008a] font-normal line-clamp-3">
                                {value.description}
                              </div>
                            </div>
                            <div className="h-[3.4rem] xl:h-[3.4rem] 2xl:h-[3.8rem] w-full flex items-end">
                              <div className="w-full h-auto space-y-0.5">
                                <div className="w-full h-auto flex text-[10px]">
                                  <div className="flex flex-auto text-[#0000008a]">
                                    Assigned on: {value.assignDate}
                                  </div>
                                  <div
                                    className="text-[#A4A029] underline cursor-pointer"
                                    onClick={() => {
                                      setPersonaInfo(!personaInfo);
                                      setPersonaInfoDetails(value);
                                    }}
                                  >
                                    {value.status}
                                  </div>
                                </div>
                                <button
                                  onClick={() => SelectionFunction(value)}
                                  className={`h-auto w-full flex justify-center rounded-[5px] py-2 xl:py-1.5 text-[12px] xl:text-[10px] 2xl:text-[12px] cursor-pointer ${
                                    selected?.title == value.title
                                      ? "bg-[#F68D1E] text-[#EEF8FB]"
                                      : "border border-[#F68D1E] text-[#F68D1E]"
                                  }`}
                                >
                                  {selected?.title == value.title
                                    ? "Selected"
                                    : "Select"}
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <hr className="mx-[3.5rem] xl:mx-[2rem] 2xl:mx-[3.5rem] text-[#131f4946] h-0" />
                <div className="h-[5rem] xl:h-[3rem] 2xl:h-[5rem] w-full flex justify-between items-center px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem]">
                  <button
                    onClick={() => navigate("/assigned-mode")}
                    className="h-auto w-[10rem] xl:w-[8rem] 2xl:w-[10rem] border border-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#F68D1E] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                  >
                    <img src="./leftarrow.svg" alt="LeftArrow" loading="lazy" />
                    back
                  </button>
                  <button
                    onClick={() => NavigateFunction()}
                    className="h-auto w-[10rem] xl:w-[8rem] 2xl:w-[10rem] bg-[#F68D1E] flex justify-center items-center gap-2 py-1 text-[#FFFFFF] text-[18px] xl:text-[14px] 2xl:text-[18px] rounded-[5px] cursor-pointer"
                  >
                    Next{" "}
                    <img
                      src="./rightarrow.svg"
                      alt="RightArrow"
                      loading="lazy"
                    />
                  </button>
                </div>
              </div>
              <AssignSideMenu index={5} />
            </div>
          </div>
        </div>
        {/* Persona Informatio Model */}
        <PersonaInfo
          personaInfo={personaInfo}
          setPersonaInfo={setPersonaInfo}
          personaInfoDetails={personaInfoDetails}
          setPersonaInfoDetails={setPersonaInfoDetails}
        />
        {/* <div className="absolute inset-0 h-[35.5rem] xl:h-[35.5rem] 2xl:h-[56.5rem]  w-screen mt-[58px] xl:mt-[44px] 2xl:mt-[58px]  z-20 flex justify-center items-center bg-[#00000065] backdrop-blur-[10px]">
          <div className="h-[25rem] w-[50rem] bg-[#FFFFFF] inset-shadow-[6px] rounded-[10px]">
            <div className="h-[2.5rem] w-full px-5 flex items-center">
              <div className="text-[#131F49] text-[16px] font-medium flex flex-auto">
                Persona Selection
              </div>
              <div>
                <img src="./close.svg" alt="close" />
              </div>
            </div>
            <div className="h-[22.5rem] w-full flex">
              <div className="h-full w-[18rem] px-2.5 space-y-2">
                <div className="h-[85%] w-full flex items-end">
                  <img
                    src="./coursedummy.png"
                    alt="course"
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
                  Name
                </div>
                <div className="text-[#000000d2] font-medium text-[12px]">
                  Age: 28
                </div>
                <div className="text-[#000000d2] font-medium text-[12px]">
                  Profession: UI/UX Designer
                </div>
                <div className="h-[16.3rem] w-full p-2 bg-[#7070701C] border border-[#7070701C] rounded-[10px]">
                  <div className="h-full w-full text-[#000000bb] leading-5 text-[12px] overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                    <div>Description</div>
                    <div>
                      Lorem, ipsum dolor sit amet consectetur adipisicing elit.
                      Officiis tempora consequatur doloribus, itaque voluptates
                      quas rerum adipisci, maxime assumenda molestiae delectus
                      in vel id pariatur quasi nulla dicta aut illo. Lorem,
                      ipsum dolor sit amet consectetur adipisicing elit. Non
                      minus, possimus in beatae totam sed esse reiciendis enim
                      nobis corporis aperiam, necessitatibus, commodi hic
                      suscipit. Molestias blanditiis magni dolores expedita!
                      Lorem ipsum dolor, sit amet consectetur adipisicing elit.
                      Magnam vel excepturi aliquid adipisci eum at dolor
                      assumenda omnis delectus, obcaecati accusantium nostrum
                      fugiat fuga accusamus ipsum recusandae et? Non, vitae.
                      Lorem ipsum dolor sit amet consectetur adipisicing elit.
                      Ex, reprehenderit quas laboriosam ut enim, consequatur
                      ullam unde cumque error aliquid, doloremque rem modi rerum
                      illo incidunt voluptatibus autem ipsa. Adipisci!
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div> */}
      </div>
    </div>
  );
};

export default AssignedPersona;
