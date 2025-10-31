// // import React, { useState, useEffect } from "react";
// // import { useLOIData } from "../../store";
// // import styles from "../AvatarCreation/Voice.module.css";
// // import SelectionCard from "../../Components/Card/SelectionCard";
// // import AvatarCard from "../../Components/ModesComponent/AvatarCard";
// // import WarningIcon from "../../Icons/WarningIcon";
// // import DownloadIcon from "../../Icons/DownloadIcon";
// // import Card from "../../Components/Card/Card";
// // import VoiceCard from "../../Components/Card/VoiceCard";
// // import axios from "../../service";


// // function Voice() {
// //   let [currentPage, setCurrentPage] = useState("Create Avatar Voice Selection");
// //   let [warn, setWarn] = useState(false);
// //   const [alreadyPlaying, setAlreadyPlaying] = useState(null);
// //   const [currentPlaying, setCurrentPlaying] = useState(null);
// //   const [voiceData, setVoiceData] = useState([]);
// //   const [filteredData, setFilteredData] = useState([]);
// //   let [activeCourse, setActiveCourse] = useState("all");

// //   const { selectedData, setSelectedData } = useLOIData();

// //   useEffect(() => {
// //     const fetchVoices = async () => {
// //       try {
// //         const Auth = localStorage.getItem("migoto-cms-token");
// //         const headers = {
// //           "Content-Type": "application/json",
// //           authorization: Auth,
// //         };

// //         const result = await axios.get("/bot-voices/?skip=0&limit=100", { headers });
// //         setVoiceData(result.data);
// //         setFilteredData(result.data); // Ensure this is an array
// //       } catch (error) {
// //         console.error("Error fetching bot voices:", error);
// //       }
// //     };

// //     fetchVoices();
// //   }, []);

// //   const handleChangeCourse = (creator) => {
// //     setActiveCourse(creator);
// //     if (creator === "all") {
// //       setFilteredData(voiceData);
// //     } else {
// //       setFilteredData(voiceData.filter((item) => item.created_by === creator));
// //     }
// //   };

// //   return (
// //     <>
// //       <div className={styles.pageHeader}>
// //         <div className={styles.activePage}>
// //           <p>List of Voices Available</p>
// //         </div>
// //       </div>

// //       <div className={styles.voiceOutter}>
// //         <div className={styles.voiceBody}>
// //           {filteredData.map((item, index) => (
// //             <VoiceCard
// //               data={item}
// //               key={index}
// //               currentPage={currentPage}
// //               alreadyPlaying={alreadyPlaying}
// //               setAlreadyPlaying={setAlreadyPlaying}
// //               currentPlaying={currentPlaying}
// //               setCurrentPlaying={setCurrentPlaying}
// //             />
// //           ))}
// //         </div>
// //       </div>

// //       <div className={styles.BtnGroup}>
// //         {currentPage === "PersonaSelection" && <button className={styles.cancelBtn}>Cancel</button>}
// //         {currentPage === "CoachAISelection" && (
// //           <button className={styles.backBtn} onClick={() => setCurrentPage("PersonaSelection")}>
// //             {"<"}Back
// //           </button>
// //         )}
// //         <button
// //           className={styles.nextBtn}
// //           disabled={!selectedData[currentPage]?.length > 0}
// //           onClick={() => setCurrentPage("CoachAISelection")}
// //         >
// //           Next {">"}
// //         </button>
// //       </div>
// //     </>
// //   );
// // }

// // export default Voice;


// import React, { useState, useEffect } from "react";
// import { useLOIData } from "../../store";
// import styles from "../AvatarCreation/Voice.module.css";
// import SelectionCard from "../../Components/Card/SelectionCard";
// import AvatarCard from "../../Components/ModesComponent/AvatarCard";
// import WarningIcon from "../../Icons/WarningIcon";
// import DownloadIcon from "../../Icons/DownloadIcon";
// import Card from "../../Components/Card/Card";
// import VoiceCard from "../../Components/Card/VoiceCard";
// import axios from "../../service";


// function Voice() {
//   let [currentPage, setCurrentPage] = useState("Create Avatar Voice Selection");
//   let [warn, setWarn] = useState(false);
//   const [alreadyPlaying, setAlreadyPlaying] = useState(null);
//   const [currentPlaying, setCurrentPlaying] = useState(null);
//   const [voiceData, setVoiceData] = useState([]);
//   const [filteredData, setFilteredData] = useState([]);
//   let [activeCourse, setActiveCourse] = useState("all");

//   const { selectedData, setSelectedData } = useLOIData();

//   useEffect(() => {
//     const fetchVoices = async () => {
//       try {
//         const Auth = localStorage.getItem("migoto-cms-token");
//         const headers = {
//           "Content-Type": "application/json",
//           authorization: Auth,
//         };

//         const result = await axios.get("/bot-voices/?skip=0&limit=100", { headers });
//         setVoiceData(result.data);
//         setFilteredData(result.data); // Ensure this is an array
//       } catch (error) {
//         console.error("Error fetching bot voices:", error);
//       }
//     };

//     fetchVoices();
//   }, []);

//   const handleChangeCourse = (creator) => {
//     setActiveCourse(creator);
//     if (creator === "all") {
//       setFilteredData(voiceData);
//     } else {
//       setFilteredData(voiceData.filter((item) => item.created_by === creator));
//     }
//   };

//   return (
//     <>
//       <div className={styles.pageHeader}>
//         <div className={styles.activePage}>
//           <p>List of Voices Available</p>
//         </div>
//       </div>

//       <div className={styles.voiceOutter}>
//         <div className={styles.voiceBody}>
//           {filteredData.map((item, index) => (
//             <VoiceCard
//               data={item}
//               key={index}
//               currentPage={currentPage}
//               alreadyPlaying={alreadyPlaying}
//               setAlreadyPlaying={setAlreadyPlaying}
//               currentPlaying={currentPlaying}
//               setCurrentPlaying={setCurrentPlaying}
//             />
//           ))}
//         </div>
//       </div>

//       <div className={styles.BtnGroup}>
//         {currentPage === "PersonaSelection" && <button className={styles.cancelBtn}>Cancel</button>}
//         {currentPage === "CoachAISelection" && (
//           <button className={styles.backBtn} onClick={() => setCurrentPage("PersonaSelection")}>
//             {"<"}Back
//           </button>
//         )}
//         <button
//           className={styles.nextBtn}
//           disabled={!selectedData[currentPage]?.length > 0}
//           onClick={() => setCurrentPage("CoachAISelection")}
//         >
//           Next {">"}
//         </button>
//       </div>
//     </>
//   );
// }

// export default Voice;

import React, { useState, useEffect } from "react";
import { useLOIData } from "../../store";
import styles from "../AvatarCreation/Voice.module.css";
import SelectionCard from "../../Components/Card/SelectionCard";
import AvatarCard from "../../Components/ModesComponent/AvatarCard";
import WarningIcon from "../../Icons/WarningIcon";
import DownloadIcon from "../../Icons/DownloadIcon";
import Card from "../../Components/Card/Card";
import VoiceCard from "../../Components/Card/VoiceCard";
import axios from "../../service";


function Voice() {
  let [currentPage, setCurrentPage] = useState("Create Avatar Voice Selection");
  let [warn, setWarn] = useState(false);
  const [alreadyPlaying, setAlreadyPlaying] = useState(null);
  const [currentPlaying, setCurrentPlaying] = useState(null);
  const [voiceData, setVoiceData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  let [activeCourse, setActiveCourse] = useState("all");

  const { selectedData, setSelectedData } = useLOIData();

  useEffect(() => {
    const fetchVoices = async () => {
      try {

        const result = await axios.get("/bot-voices/?skip=0&limit=100");
        setVoiceData(result.data);
        setFilteredData(result.data); // Ensure this is an array
      } catch (error) {
        console.error("Error fetching bot voices:", error);
      }
    };

    fetchVoices();
  }, []);

  const handleChangeCourse = (creator) => {
    setActiveCourse(creator);
    if (creator === "all") {
      setFilteredData(voiceData);
    } else {
      setFilteredData(voiceData.filter((item) => item.created_by === creator));
    }
  };

  return (
    <>
      <div className={styles.pageHeader}>
        <div className={styles.activePage}>
          <p>List of Voices Available</p>
        </div>
      </div>

      <div className={styles.voiceOutter}>
        <div className={styles.voiceBody}>
          {filteredData.map((item, index) => (
            <VoiceCard
              data={item}
              key={index}
              currentPage={currentPage}
              alreadyPlaying={alreadyPlaying}
              setAlreadyPlaying={setAlreadyPlaying}
              currentPlaying={currentPlaying}
              setCurrentPlaying={setCurrentPlaying}
            />
          ))}
        </div>
      </div>

      <div className={styles.BtnGroup}>
        {currentPage === "PersonaSelection" && <button className={styles.cancelBtn}>Cancel</button>}
        {currentPage === "CoachAISelection" && (
          <button className={styles.backBtn} onClick={() => setCurrentPage("PersonaSelection")}>
            {"<"}Back
          </button>
        )}
        <button
          className={styles.nextBtn}
          disabled={!selectedData[currentPage]?.length > 0}
          onClick={() => setCurrentPage("CoachAISelection")}
        >
          Save {">"}
        </button>
      </div>
    </>
  );
}

export default Voice;
