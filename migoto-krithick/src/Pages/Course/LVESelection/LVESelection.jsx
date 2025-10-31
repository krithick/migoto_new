import React, { useEffect, useState, useRef } from "react";
import styles from '../LVESelection/LVESelection.module.css';
import { useNavigate } from "react-router-dom";
import PersonaSelection from "../../AvatarCreation/PersonaSelection";
import Voice from "../../AvatarCreation/Voice";
import Environment from "../LVESelection/Environment";
import Language from "./Language";
import { useLangStore, useLOIData, useModeData, usePreviewStore, useUserPopupStore } from "../../../store";
import axios from '../../../service';
import LVEVoice from "./LVEVoice";
import { BaseURL6445, BaseURL7445 } from "../../../helper";
import { clearAllData, clearScenarioData, getSessionStorage, setSessionStorage } from "../../../sessionHelper";
function LVESelection({}) {
  const { message, setMessage } = useUserPopupStore();
  const { selectedData, setSelectedData } = useLOIData();
  let {userPopup,setUserPopup} = useUserPopupStore()
  let [activeState, setActiveState] = useState("Language");
  let [datas, setDatas] = useState([]);
  let [data, setData] = useState(datas);
  let [overallData, setOverallData] = useState([]);
  let [voiceData, setVoiceData] = useState([])
  let [languageData, setLanguageData] = useState([])
  let [environmentData, setEnvironmentData] = useState([])
  let navigate = useNavigate()
  let flow = localStorage.getItem("flow")
  const { localLang, setLocalLang } = useLangStore();
  const { isPreview, setIsPreview } = usePreviewStore();
  
  // V2: Prompt generation state
  const [isGeneratingPrompts, setIsGeneratingPrompts] = useState(false);
  const [promptProgress, setPromptProgress] = useState({});
  const eventSourceRef = useRef(null);

  function filterVoicesByAllowedLanguages(voices, allowedLanguages) {
    return voices.filter(voice => allowedLanguages?.includes(voice.language_code));
  }
    const fetchLanguage = () => {
    axios
    .get(`/languages/`)
    .then((res) => {
      setLanguageData(res.data,"languages")
      setSelectedData("Language",[res.data[0].code]);
      setLocalLang([res.data[0].id])
    })
    .catch((err) => {
      console.log("err: ", err);
    });
    axios
    .get(`/environments/`)
    .then((res) => {
      setEnvironmentData(res.data,"environments")
      setSelectedData("Environment",res.data.map((item)=>item.id));

    })
    .catch((err) => {
      console.log("err: ", err);
    });

    }

    const fetchVoice = () => {
      axios
      .get(`/bot-voices/`)
      .then((res) => {
        const allowedLanguages = selectedData["Language"]; // An array of allowed language codes
        const filteredVoices = filterVoicesByAllowedLanguages(res.data, allowedLanguages);    
        setVoiceData(filteredVoices);
        setSelectedData("Voice",filteredVoices.map((item)=>item.id));
      })
      .catch((err) => {
        console.log("err:", err);
      });

    }    

    useEffect(()=>{
      if(selectedData["Language"]?.length>0){
        fetchVoice()
      }else{
        setSelectedData("Voice",[])
      }
    },[selectedData["Language"]])
    useEffect(()=>{
        fetchLanguage()
    },[])

    const createModePayloads = (basePayload) => {
    const modes = ["learn_mode", "try_mode", "assess_mode"];
    return modes.map((mode) => ({
    ...basePayload,
    mode,
    }));
    };
        
    const handleAssignCourseToUser = async(id,userId) => {

      let finalUserIds;
      if(userId && userId?.length>0) {
        finalUserIds = userId; 
      }else{
        finalUserIds = getSessionStorage("createdUser");
      }

      if (!finalUserIds || finalUserIds?.length === 0) {
        setMessage({
          enable: true,
          msg: "No users selected",
          state: false,
        });
        return;
      }
    
      const courseId = selectedData["courseId"]?selectedData["courseId"]:sessionStorage.getItem("courseId");
      const moduleId = selectedData["moduleId"]?selectedData["moduleId"]:sessionStorage.getItem("moduleId");
      const scenarioId = id;
    
      const getEnabledModes = () => {
        const modes = [];

        modes.push("learn_mode");
        modes.push("try_mode");
        modes.push("assess_mode");

        return modes;
      };

      const payload = {
        user_ids: finalUserIds,
        include_all_modules: false,
        include_all_scenarios: false,
        module_ids: [moduleId],
        scenario_mapping: {
          [moduleId]: [id]
        },
        mode_mapping: {
          [id]: getEnabledModes()
        }
      };

      try {
        const response = await axios.post(
          `/course-assignments/course/${courseId}/assign-with-content`,
          payload
        );
        setMessage({
          enable: true,
          msg: "Course Assigned Successfully",
          state: true,
        })
        localStorage.setItem("currentPathLocation", "Dashboard");
        setSelectedData("createdUser",null)
        navigate("/migoto-cms/dashboard");
        // window.location.reload()
      } catch (error) {
        console.error("Assignment failed:", error.response?.data || error.message);
        setMessage({
          enable: true,
          msg: "Something went wrong...",
          state: false,
        })
      }
    }


    const handleAssignCourse = async (userId) => {
      
      if(!isValid){
        setMessage({
          enable: true,
          msg: "Kindly Provide Valid data of Language and Environment",
          state: false,
        })
        return
      }

      setIsGeneratingPrompts(true);
      setPromptProgress({ status: 'Starting prompt generation...' });

      try {
        // V2: Get persona (1 persona for try+assess, learn has no persona)
        const tryAssessPersonaId = getSessionStorage("try_assess_persona_id");
        const templateId = getSessionStorage("template_id");
        
        if (!tryAssessPersonaId) {
          throw new Error("Try/Assess persona not found");
        }

        // V2: Start async prompt generation (learn sync + try/assess async)
        const promptGenResponse = await axios.post("/scenario/v2/generate-final-prompts", {
          template_id: templateId,
          try_assess_persona_id: tryAssessPersonaId
        });

        const jobId = promptGenResponse.data.job_id;
        const learnPrompt = promptGenResponse.data.learn_prompt;  // Learn prompt returned immediately
        
        // V2: Connect to SSE for progress updates
        const eventSource = new EventSource(`${BaseURL6445}scenario/v2/prompt-generation-status/${jobId}`);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = async (event) => {
          const data = JSON.parse(event.data);
          
          if (data.type === 'persona_progress') {
            setPromptProgress(prev => ({
              ...prev,
              [data.persona_id]: data.status
            }));
          }
          
          if (data.type === 'results') {
            eventSource.close();
            setIsGeneratingPrompts(false);
            
            // V2: Use learn_prompt from initial response, create avatar_interactions
            await createAvatarInteractionsV2(tryAssessPersonaId, learnPrompt, userId);
          }
          
          if (data.type === 'status_update' && data.status === 'failed') {
            eventSource.close();
            setIsGeneratingPrompts(false);
            setMessage({
              enable: true,
              msg: data.error || 'Prompt generation failed',
              state: false,
            });
          }
        };

        eventSource.onerror = () => {
          eventSource.close();
          setIsGeneratingPrompts(false);
          setMessage({
            enable: true,
            msg: "Connection error during prompt generation",
            state: false,
          });
        };

      } catch (error) {
        setIsGeneratingPrompts(false);
        setMessage({
          enable: true,
          msg: error.message || "Failed to generate prompts",
          state: false,
        });
      }
    };

    const createAvatarInteractionsV2 = async (tryAssessPersonaId, learnPrompt, userId) => {
      try {
        const base = {
          avatars: getSessionStorage("avatarSelection"),
          languages: localLang,
          bot_voices: selectedData["Voice"],
          environments: selectedData["Environment"],
          layout: getSessionStorage("Layout")?getSessionStorage("Layout"):1,
          assigned_documents: Array.isArray(getSessionStorage("Document")) 
            ? getSessionStorage("Document") 
            : [],
          assigned_videos: Array.isArray(getSessionStorage("Video")) 
            ? getSessionStorage("Video") 
            : [],
          content: {}
        };

        const payloads = [
          {
            ...base,
            bot_role: "trainer",
            bot_role_alt: "employee",
            system_prompt: learnPrompt,  // Immediate from API
            persona_id: null,  // Learn mode has no persona
            mode: "learn_mode"
          },
          {
            ...base,
            bot_role: "employee",
            bot_role_alt: "evaluatee",
            system_prompt: null,  // Fetched from persona during chat
            persona_id: tryAssessPersonaId,  // Same persona for try+assess
            mode: "try_mode"
          },
          {
            ...base,
            bot_role: "employee",
            bot_role_alt: "evaluatee",
            system_prompt: null,  // Fetched from persona during chat
            persona_id: tryAssessPersonaId,  // Same persona for try+assess
            mode: "assess_mode"
          }
        ];
        
        const collectedIds = [];
        const tempSelectedData = {
          scenarioData: selectedData["scenarioData"],
          "moduleId": getSessionStorage("moduleId")
        };

        for (const payload of payloads) {
          const res = await axios.post("/avatar-interactions/", payload)
          const id = res.data.id;

          if (payload.mode) {
            tempSelectedData[`${payload.mode}Id`] = id;
            setSelectedData(`${payload.mode}Id`, id);
          }

          collectedIds.push(id);
        }

        if (collectedIds.length == 3) {
          const finalPayload = {
            title: getSessionStorage("scenarioData")?.title,
            description: getSessionStorage("scenarioData")?.description,
            thumbnail_url: getSessionStorage("scenarioData")?.thumbnail_url,
            template_id:getSessionStorage("template_id"),
            learn_mode: {
              avatar_interaction: collectedIds[0]
            },
            try_mode: {
              avatar_interaction: collectedIds[1]
            },
            assess_mode: {
              avatar_interaction: collectedIds[2]
            }
          };

          const scenarioRes = await axios.post(`${BaseURL6445}modules/${tempSelectedData["moduleId"]}/scenarios`, finalPayload)
          setMessage({
            enable: true,
            msg: "Scenario Created Successfully",
            state: true,
          })
          setSelectedData("scenarioId",scenarioRes.data?.id);
          
          if(flow == "Create Course flow" || flow == "Create User and Course flow"){
            handleAssignCourseToUser(scenarioRes.data.id, userId)
          }
          if(flow == "CourseManagement flow"){
            navigate('/migoto-cms/courseManagement')
          }
          clearAllData()
        }
      } catch (err) {
        setMessage({
          enable: true,
          msg: err.message || "Something went wrong",
          state: false,
        })
      }
    };

    let isValid = (selectedData["Language"]?.length>0 && selectedData["Voice"]?.length>0 && selectedData["Environment"]?.length>0)

    const handlePopUp = () => {
      if(!isValid){
        setMessage({
          enable: true,
          msg: "Kindly Provide Valid data of Language and Environment",
          state: false,
        })
        return
      }
        let result = new Promise((resolve) => {
          setIsPreview({
            enable: true,
            msg: ``,
            value: "userListPopUp",
            resolve,
          });
        });
        result.then((res) => {
          let aRes = res
          if (!aRes || aRes === false) return;
          setSessionStorage("createdUser", aRes)
          setSelectedData("createdUser", aRes);
          // use res directly here instead of waiting for Zustand update
          handleAssignCourse(aRes);
        });
    }
  return (
    <div className={styles.avatarContainer}>
      <div className={styles.avatarHeader1}>
        <div className={styles.avatarHeaderLeft}>
          <p>Avatar Details</p>
        </div>
      </div>
      {/* -------------------Body--------------- */}
      {/*  sidebar */}
      <div className={styles.OverallContainer}>
      <div className={styles.sideBar}>
        <div
          className={`${styles.unselected} ${
            activeState == "Language"|| activeState =="Language" ? styles.selected : ""
          }`}
          onClick={() => {
            setActiveState("Language");
          }}
        >
          Language
        </div>
        {/* <div
          className={`${styles.unselected} ${
            activeState == "Voice" ? styles.selected : ""
          }`}
          onClick={() => {
            setActiveState("Voice");
          }}
        >
          Voice
        </div> */}
        <div
          className={`${styles.unselected} ${
            activeState == "Environment" ? styles.selected : ""
          }`}
          onClick={() => {
            setActiveState("Environment");
          }}
        >
          Environment
        </div>
      </div>

    <div className={styles.ContainerContent}>
      {activeState == "Language" && <Language data={languageData}/>}
      {activeState == "Environment" && <Environment data={environmentData} />}
      {/* {activeState == "Voice" && <LVEVoice data={voiceData}/>} */}
    </div>
      </div>
      <div className={styles.BtnGroup}>
        {<button className={styles.nextBtn} onClick={()=>{navigate(-1)}} disabled={isGeneratingPrompts}>Cancel</button>}
        {flow !="Create Course flow"&&<button className={styles.nextBtn} onClick={()=>{handleAssignCourse()}} disabled={isGeneratingPrompts}>{isGeneratingPrompts ? 'Generating Prompts...' : 'Assign Course'}</button>}
        {flow =="Create Course flow" && selectedData["createdUser"]?.length>0 &&<button className={styles.nextBtn} onClick={()=>{handleAssignCourse()}} disabled={isGeneratingPrompts}>{isGeneratingPrompts ? 'Generating Prompts...' : 'Assign Course to User'}</button>}
        {flow =="Create Course flow"&& !selectedData["createdUser"]?.length>0 &&<button className={styles.nextBtn} onClick={()=>{handlePopUp()}} disabled={isGeneratingPrompts}>Select User</button>}
      </div>
      {isGeneratingPrompts && (
        <div className={styles.progressOverlay}>
          <div className={styles.progressCard}>
            <h3>Generating AI Prompts...</h3>
            <p>{promptProgress.status || 'Processing...'}</p>
            {Object.entries(promptProgress).filter(([k]) => k !== 'status').map(([personaId, status]) => (
              <div key={personaId} className={styles.progressItem}>
                <span>{personaId}:</span> <span>{status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default LVESelection;
