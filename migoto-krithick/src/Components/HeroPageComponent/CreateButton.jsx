import React, { useEffect, useRef, useState } from "react";
import styles from "../../Pages/HeroPage/HeroPage.module.css";
import PersonIcon from "../../Icons/PersonIcon";
import CourseIcon from "../../Icons/CourseIcon";
import CreateAvatarIcon from "../../Icons/CreateAvatarIcon";
import { useLOIData } from "../../store";
import { useNavigate } from "react-router-dom";
import { TimeLineRoute } from "../../RouteHelper/TimeLineRoute";
import { clearAllData, clearScenarioData } from "../../sessionHelper";

function CreateButton({ setCurrentPathLocation }) {
  const [openCreatBox, setOpenCreatBox] = useState(false);
  const createButtonsRef = useRef(null);
  const { selectedData, setSelectedData, setClean } = useLOIData();
  const navigate = useNavigate();
  let checkPath = localStorage.getItem("currentPathLocation");

  useEffect(() => {
    document.addEventListener("mousedown", (e) => {
      if (
        createButtonsRef.current &&
        !createButtonsRef.current.contains(e.target)
      ) {
        setOpenCreatBox(false);
      }
    });
  }, []);

  const handleCreateSection = (data) => {
    setCurrentPathLocation(localStorage.setItem("currentPathLocation", data));
    setOpenCreatBox(!openCreatBox);
    localStorage.setItem("flow", `${data} flow`);
  };
  const downloadAudio = async () => {
    const token = "2FZZ5VCWWNIRNZOJ3RPVUHBESVL2NAYQ"; // Replace with your Wit.ai token
    const apiUrl = "https://api.wit.ai/synthesize?v=20240304";

    // The data to send in the POST request
    const requestData = {
      // q: "It’s a busy Monday morning at the bank. Mr. Suresh, a regular customer, approaches the counter to collect a demand draft he had requested two days ago. When he receives the draft, the officer on duty, Ms. Kavita, informs him of the applicable service charges.",
      q:
        // q: props, // Replace with dynamic text if needed
        // "It is a Friday afternoon, and the bank is crowded as many customers are withdrawing money before the weekend. The cashier, Mr. Arun, is following the token system to serve customers in order.Suddenly, Mr. Ravi, a middle-aged man, rushes to the counter without a token and demands an urgent cash withdrawal of ₹2 lakh. He looks visibly anxious and says,I have a medical emergency, and I need this cash immediately! I don’t have time to wait for a token!Mr. Arun, maintaining protocol, replies, Sir, we have a long queue, and we are following the token system. Please take a token, and your turn will come shortly."
        "Mr. Ravi becomes agitated and raises his voice, attracting attention from other customers. He insists,This is ridiculous! You should understand my urgency. If something happens to my relative because of this delay, will you take responsibility?The other customers start murmuring, some sympathizing with Mr. Ravi and others demanding fairness. The tension in the branch escalates.At this moment, as the Branch Manager, you step in to manage the situation",
      // ,voice: "wit$Cooper", // You can choose another voice from available options in Wit.ai
      voice: "wit$Rebecca",
      speed: 90,
      pitch: 90,
    };

    try {
      // Sending the POST request to Wit.ai API
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "audio/mpeg", // Expected audio format (MP3)
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error("Failed to get audio from Wit.ai");
      }

      // The response body contains the audio in MPEG format (MP3)
      const audioBlob = await response.blob();
      const AUDIOURL = URL.createObjectURL(audioBlob);

      // Create download link
      const downloadLink = document.createElement("a");
      downloadLink.href = AUDIOURL;
      downloadLink.download = "audio.mp3"; // Set desired filename
      downloadLink.click();
    } catch (err) {
      console.log(err);
    }
  };

  const playArabic = () => {
    const utterance = new SpeechSynthesisUtterance("السلام عليكم، كيف حالك؟");
    utterance.lang = "ar-SA"; // Arabic
    speechSynthesis.speak(utterance);
  };

  function speakArabic(text) {
    // Stop any current speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "ar-SA"; // Arabic (Saudi Arabia)
    utterance.rate = 1;       // Speed (0.5 - 2)
    utterance.pitch = 1;      // Pitch (0 - 2)
    utterance.volume = 1;     // Volume (0 - 1)

    // Optional: Pick an Arabic voice (if multiple installed)
    const voices = window.speechSynthesis.getVoices();
    const arabicVoice = voices.find(v => v.lang.startsWith("ar"));
    if (arabicVoice) utterance.voice = arabicVoice;

    window.speechSynthesis.speak(utterance);
  }

  // useEffect(() => {
  //   window.speechSynthesis.onvoiceschanged = () => {
  //     console.log(
  //       "Arabic voices loaded:",
  //       window.speechSynthesis.getVoices().filter(v => v.lang.startsWith("ar"))
  //     );
  //   };
  // }, []);

  return (
    <>
      {checkPath == "Dashboard" && (
        <button
          className={styles.createBtn}
          onClick={() => {
            setOpenCreatBox(!openCreatBox);
            // downloadAudio()
            // speakArabic("السلام عليكم، كيف حالك؟");
          }}
        >
          Create +{" "}
        </button>
      )}
      {openCreatBox && (
        <div className={styles.createBox} ref={createButtonsRef}>
          <div
            onClick={() => {
              localStorage.setItem(
                "TLData",
                JSON.stringify(TimeLineRoute["/migoto-cms/createUser"])
              );
              handleCreateSection("Create User"),
                navigate("/migoto-cms/createUser"),
                setSelectedData("avatarSelection", null);
              setSelectedData("ListofAvatars", null);
              setSelectedData("createdUser", []);
              clearAllData();
              localStorage.setItem("timeLine", JSON.stringify(true));
            }}
          >
            {" "}
            <PersonIcon />
            Create User
          </div>
          <div
            onClick={() => {
              localStorage.setItem(
                "TLData",
                JSON.stringify(TimeLineRoute["/migoto-cms/createCourse"])
              );
              handleCreateSection("Create Course"),
                navigate("/migoto-cms/createCourse"),
                setSelectedData("avatarSelection", null);
              setSelectedData("ListofAvatars", null);
              setSelectedData("createdUser", []);
              clearAllData();
              localStorage.setItem("timeLine", JSON.stringify(true));
            }}
          >
            {" "}
            <CourseIcon />
            Create Course
          </div>
          <div
            onClick={() => {
              localStorage.setItem(
                "TLData",
                JSON.stringify(TimeLineRoute["/migoto-cms/selectScenario"])
              );
              handleCreateSection("Create Avatar"),
                navigate("/migoto-cms/selectScenario");
              setSelectedData("List Of Courses", null);
              setSelectedData("List Of Modules", null);
              setSelectedData("List Of Scenario", null);
              clearAllData();
              localStorage.setItem("timeLine", JSON.stringify(true));
            }}
          >
            {" "}
            <CreateAvatarIcon /> Create Avatar
          </div>
        </div>
      )}
    </>
  );
}

export default CreateButton;
