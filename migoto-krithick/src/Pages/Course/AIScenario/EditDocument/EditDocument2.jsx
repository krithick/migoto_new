import React, { useState } from "react";
import styles from "../EditDocument/EditDocument.module.css";
import BackIcon from "../../../../Icons/BackIcon";
import AddIcon from "../../../../Icons/AddIcon";
import SectionCategoryPopup from "../../../User/SectionCategoryPopup/SectionCategoryPopup";
import { useLOIData, useUserPopupStore } from "../../../../store";
import { div } from "three/tsl";
import PlusIcon from "../../../../Icons/PlusIcon";
import axios from "../../../../service";
import { BaseURL6445 } from "../../../../helper";
import { useNavigate } from "react-router-dom";
import { getSessionStorage } from "../../../../sessionHelper";
import { usePreviewStore } from "../../../../store";
import AddPrompt from "./AddPrompt";
import DeleteIcon from "../../../../Icons/DeleteIcon";

function EditDocument2({ setEditPage, setCurrentPage }) {
  let [selected, setSelected] = useState("General Info");
  let { selectedData, setSelectedData } = useLOIData();
  const { message, setMessage } = useUserPopupStore();
  const { isPreview, setIsPreview } = usePreviewStore();
  let navigate = useNavigate();

  //for content section
  const [categoryStatus, setCategoryStatus] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sectionStatus, setSectionStatus] = useState(false);
  const [editStatus, setEditStatus] = useState(false);

  const [General, setGeneral] = useState(
    selectedData["EditResponse"]?.general_info
  );
  const [Feedback, setFeedback] = useState(
    selectedData["EditResponse"]?.feedback_mechanism
  );
  const [Context, setContext] = useState(
    selectedData["EditResponse"]?.context_overview
  );
  const [KnowledgeBase, setKnowledgeBase] = useState(
    selectedData["EditResponse"]?.knowledge_base
  );
  const [Persona, setPersona] = useState(
    selectedData["EditResponse"]?.persona_definitions
  );
  const [templateData, setTemplateData] = useState(
    selectedData["EditResponse"]
  );

  const handleEditPoint = async (section, subsection, index, newValue) => {
    // Update local state immediately
    setTemplateData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [subsection]: prev[section][subsection].map((item, i) =>
          i === index ? newValue : item
        ),
      },
    }));
    setEditStatus(true)
  };

  const handleAddPoint = async (section, subsection) => {
    let result = await new Promise((resolve) => {
      setIsPreview({
        enable: true,
        msg: subsection,
        value: "addPrompt",
        resolve,
      });
    });
    
    if (result && result.trim()) {
      try {
        const response = await fetch(
          `${BaseURL6445}add-remove-points`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              section: section,
              subsection: subsection,
              action: "add",
              point_data: { content: result.trim() },
              current_template: templateData,
            }),
          }
        );

        if (response.ok) {
          const data = await response.json();
          setTemplateData(data.updated_template);
          setEditStatus(true)
        } else {
          throw new Error("Failed to add point");
        }
      } catch (error) {
        console.error("Error adding point:", error);
        // Fallback to local update
        setTemplateData((prev) => ({
          ...prev,
          [section]: {
            ...prev[section],
            [subsection]: [...(prev[section][subsection] || []), result.trim()],
          },
        }));
      }
    }
  };

  const handleRemovePoint = async (section, subsection, index) => {
    try {
      const response = await fetch(
        `${BaseURL6445}add-remove-points`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            section: section,
            subsection: subsection,
            action: "remove",
            point_data: { index: index },
            current_template: templateData,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTemplateData(data.updated_template);
        setEditStatus(true)
      } else {
        throw new Error("Failed to remove point");
      }
    } catch (error) {
      console.error("Error removing point:", error);
      // Fallback to local update
      setTemplateData((prev) => ({
        ...prev,
        [section]: {
          ...prev[section],
          [subsection]: prev[section][subsection].filter((_, i) => i !== index),
        },
      }));
    }
  };

  const sections = [
    {
      key: "dos",
      title: "Do's",
      description: "Best practices and recommended actions",
    },
    {
      key: "donts",
      title: "Don'ts",
      description: "Things to avoid or discourage",
    },
    {
      key: "key_facts",
      title: "Key Facts",
      description: "Important information and facts",
    },
    {
      key: "conversation_topics",
      title: "Conversation Topics",
      description: "Topics to explore during interaction",
    },
  ];

  const Metricesections = [
    {
      key: "kpis_for_interaction",
      title: "kpis_for_interaction",
      description: "Best practices and recommended actions",
    },
   
  ];

  const handleSubmitData = () => {
    let tData = {
      ...templateData,
      general_info: General,
      feedback_mechanism: Feedback,
      context_overview: Context,
    };
    const isEqual = JSON.stringify(tData) === JSON.stringify(templateData);

    if (!isEqual || editStatus) {
      setTemplateData(tData);
      handlePromptSubmission(tData);
    } else {
      setEditPage("suportDocument");
    }
  };

  const handlePromptSubmission = async (promptData) => {
    try {
      const res = await axios.put(
        `scenarios-editor/${getSessionStorage("showScenario")}/template-data`,
        { ...promptData }
      );
      handleEditData(res.data)
    } catch (err) {
      console.error("Prompt submission failed:", err);
      setMessage({
        enable: true,
        msg: "Something Went Wrong",
        state: false,
      })
    }
  };

  const handleEditData = async() => {
    let payload = {
      modes_to_regenerate: [
          "learn_mode",
          "assess_mode",
          "try_mode"
      ],
      regenerate_personas: true
  }
    try {
      const res = await axios.post(
        `scenarios/${getSessionStorage("showScenario")}/regenerate`,
        { payload }
      );
      setSelectedData("updatedprompts", res.data.generated_prompts);
      handleAvatarInteraction(res.data.generated_prompts)
    } catch (err) {
      setLoading(false);
      console.error("Prompt submission failed:", err);
      setMessage({
        enable: true,
        msg: "Something Went Wrong",
        state: false,
      })
    }
  }

  const handleAvatarInteraction = async (data) => {
    const requests = [];
  
    if (selectedData["LearnModeAvatarInteractionId"]) {
      requests.push(
        axios.put(`/avatar-interactions/${getSessionStorage["LearnModeAvatarInteractionId"]}`, {
          system_prompt: data?.learn_mode,
        })
      );
    }
  
    if (selectedData["TryModeAvatarInteractionId"]) {
      requests.push(
        axios.put(`/avatar-interactions/${getSessionStorage["TryModeAvatarInteractionId"]}`, {
          system_prompt: data?.try_mode,
        })
      );
    }
  
    if (selectedData["AssessModeAvatarInteractionId"]) {
      requests.push(
        axios.put(`/avatar-interactions/${getSessionStorage["AssessModeAvatarInteractionId"]}`, {
          system_prompt: data?.assess_mode,
        })
      );
    }
  
    try {
      await Promise.all(requests);
      setEditPage("suportDocument")
    } catch (err) {
      console.error("Failed to update avatar interactions:", err);
    }
  };

  // const handleCreateAvatar = () => {
  //   setSelectedData("personaCreated",1)
  //   let template_id = selectedData["templateData"]?.template_id;
  //   setSelectedData("template_id",template_id)
  //   navigate("createAvatar")
  //   setIsPreview({enable:true,msg:[],value:"PersonaPopUp"})
  // }
  
  return (
    <>
      {/* {loading && <Loader />} */}
      <AddPrompt />
      <div className={styles.mainBox}>
        <div className={styles.mainHeader}>
          {/* <BackIcon /> */}
          <p>Edit Document</p>
        </div>
        <div className={styles.mainSection}>
          <div className={styles.sectionSidebar}>
            <div
              className={`${styles.unselected} ${
                selected == "General Info" ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected("General Info");
              }}
            >
              General Info
            </div>

            <div
              className={`${styles.unselected} ${
                selected == "Knowledge Base" ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected("Knowledge Base");
              }}
            >
              Knowledge Base
            </div>

            {/* <div
              className={`${styles.unselected} ${
                selected == "Personas" ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected("Personas");
              }}
            >
              Personas
            </div> */}

            <div
              className={`${styles.unselected} ${
                selected == "Feedback" ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected("Feedback");
              }}
            >
              Feedback
            </div>

            <div
              className={`${styles.unselected} ${
                selected == "Context" ? styles.selected : ""
              }`}
              onClick={() => {
                setSelected("Context");
              }}
            >
              Context Overview
            </div>
            <div
              className={`${styles.unselected} ${
                selected == "Success Metrics" ? styles.selected : ""
              }`}
              onClick={() => {

                // console.log('Metricesections["kpis_for_interaction"]: ', templateData.success_metrics["kpis_for_interaction"]);

                setSelected("Success Metrics");
              }}
            >
              Success Metrics
            </div>
          </div>
          {/* {----------------------} */}
          <div className={styles.sectionContent}>
            <div className={styles.contentHeader}>{selected}</div>
            <div className={styles.sectionWrapper}>
              {selected === "General Info" &&
                Object.entries(General || {}).map(([key, value]) => (
                  <div className={styles.contentForm}>
                    <div className={styles.formTop}>
                      <div key={key}>
                        {key?.replaceAll(/[_-]/g, " ")?.replace(/\b\w/g, (char) => char?.toUpperCase())}
                      </div>
                      <input
                        type="text"
                        value={value}
                        onChange={(e) =>
                          setGeneral((prev) => ({
                            ...prev,
                            [key]: e.target.value,
                          }))
                        }
                        className={styles.input}
                      />
                    </div>
                  </div>
                ))}
              {selected === "Knowledge Base" && (
                <div className={styles.container}>
                  {sections.map(({ key, title, description }) => (
                    <div key={key} className={styles.card}>
                      <div className={styles.header}>
                        <div>
                          <h4 className={styles.title}>{title}</h4>
                          <p className={styles.description}>{description}</p>
                        </div>
                        <button
                          onClick={() => handleAddPoint("knowledge_base", key)}
                          className={styles.addButton}
                        >
                          <PlusIcon className="w-4 h-4" />
                          Add {title?.replaceAll(/[_-]/g, " ")}
                        </button>
                      </div>

                      <div className={styles.pointList}>
                        {(templateData?.knowledge_base?.[key] || [])?.map(
                          (item, index) => (
                            <div key={index} className={styles.pointItem}>
                              <div className={styles.pointIndex}>
                                {index + 1}
                              </div>
                              <input
                                type="text"
                                value={item}
                                onChange={(e) =>
                                  handleEditPoint(
                                    "knowledge_base",
                                    key,
                                    index,
                                    e.target.value
                                  )
                                }
                                className={styles.input}
                              />
                              <button
                                onClick={() =>
                                  handleRemovePoint(
                                    "knowledge_base",
                                    key,
                                    index
                                  )
                                }
                                className={styles.removeButton}
                              >
                                <DeleteIcon />
                              </button>
                            </div>
                          )
                        )}
                        {(!templateData?.knowledge_base?.[key] ||
                          templateData.knowledge_base[key]?.length === 0) && (
                          <div className={styles.emptyState}>
                            No {title?.toLowerCase()?.replaceAll(/[_-]/g, " ")} added yet. Click "Add{" "}
                            {title?.slice(0, -1)?.replaceAll(/[_-]/g, " ")}" to get started.
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {selected === "Feedback" &&
                Object.entries(Feedback || {}).map(([key, value]) => (
                  <div className={styles.contentForm}>
                    <div className={styles.formTop}>
                      <div key={key}>
                        {key?.replace(/_/g, " ")?.replace(/\b\w/g, (char) => char?.toUpperCase())}
                      </div>
                      <input
                        type="text"
                        value={value}
                        onChange={(e) =>
                          setFeedback((prev) => ({
                            ...prev,
                            [key]: e.target.value,
                          }))
                        }
                        className={styles.input}
                      />
                    </div>
                  </div>
                ))}

  {/* ---------------------- */}
                  {selected === "Success Metrics" && (
                    <div className={styles.container}>
                      {
                        Metricesections.map(({ key, title, description }) => (
                          <div key={key} className={styles.card}>
                            <div className={styles.header}>
                              <div>
                                <h4 className={styles.title}>{title?.replaceAll(/[_-]/g, " ")}</h4>
                                <p className={styles.description}>
                                  {description}
                                </p>
                              </div>
                              <button
                                onClick={() =>
                                  handleAddPoint("success_metrics", key)
                                }
                                className={styles.addButton}
                              >
                                <PlusIcon className="w-4 h-4" />
                                Add {title?.replaceAll(/[_-]/g, " ")}
                              </button>
                            </div>

                            <div className={styles.pointList}>
                             
                              {(
                                templateData?.success_metrics?.[key] || []
                              )?.map((item, index) => (
                                <div key={index} className={styles.pointItem}>
                                  <div className={styles.pointIndex}>
                                    {index + 1}
                                  </div>
                                  <input
                                    type="text"
                                    value={item}
                                    onChange={(e) =>
                                      handleEditPoint(
                                        "success_metrics",
                                        key,
                                        index,
                                        e.target.value
                                      )
                                    }
                                    className={styles.input}
                                  />
                                  <button
                                    onClick={() =>
                                      handleRemovePoint(
                                        "success_metrics",
                                        key,
                                        index
                                      )
                                    }
                                    className={styles.removeButton}
                                  >
                                    <DeleteIcon />
                                  </button>
                                </div>
                              ))}
                              {(!templateData?.success_metrics?.[key] ||
                                templateData.success_metrics[key]?.length ===
                                  0) && (
                                <div className={styles.emptyState}>
                                  No {title?.toLowerCase()?.replaceAll(/[_-]/g, " ")} added yet. Click "Add{" "}
                                  {title?.replaceAll(/[_-]/g, " ")}" to get started.
                                </div>
                              )}
                            </div>
                          </div>
                          )
                        )}
                    </div>
                  )}



              {selected === "Personas" && (
                <div className={styles.container}>
                  {/* Learn Mode Persona */}
                  <div className={styles.card}>
                    <h4 className={styles.learnTitle}>Learn Mode Expert</h4>
                    <div className={styles.fieldGroup}>
                      <div>
                        <label className={styles.label}>Role</label>
                        <input
                          type="text"
                          //   value={Persona?.learn_mode_ai_bot?.role || ""}
                          className={styles.input}
                          value={
                            templateData?.persona_definitions?.learn_mode_ai_bot
                              ?.role || ""
                          }
                          onChange={(e) =>
                            setTemplateData((prev) => ({
                              ...prev,
                              persona_definitions: {
                                ...prev.persona_definitions,
                                learn_mode_ai_bot: {
                                  ...prev.persona_definitions
                                    ?.learn_mode_ai_bot,
                                  role: e.target.value,
                                },
                              },
                            }))
                          }
                        />
                      </div>
                      <div>
                        <label className={styles.label}>Background</label>
                        <textarea
                          //   value={Persona?.learn_mode_ai_bot?.background || ""}
                          className={styles.textarea}
                          value={
                            templateData?.persona_definitions?.learn_mode_ai_bot
                              ?.background || ""
                          }
                          onChange={(e) =>
                            setTemplateData((prev) => ({
                              ...prev,
                              persona_definitions: {
                                ...prev.persona_definitions,
                                learn_mode_ai_bot: {
                                  ...prev.persona_definitions
                                    ?.learn_mode_ai_bot,
                                  background: e.target.value,
                                },
                              },
                            }))
                          }
                        />
                      </div>
                      <div>
                        <label className={styles.label}>
                          Behavioral Traits
                        </label>
                        <input
                          type="text"
                          className={styles.input}
                          value={
                            templateData?.persona_definitions?.learn_mode_ai_bot
                              ?.behavioral_traits || ""
                          }
                          onChange={(e) =>
                            setTemplateData((prev) => ({
                              ...prev,
                              persona_definitions: {
                                ...prev.persona_definitions,
                                learn_mode_ai_bot: {
                                  ...prev.persona_definitions
                                    ?.learn_mode_ai_bot,
                                  behavioral_traits: e.target.value,
                                },
                              },
                            }))
                          }
                        />
                      </div>
                    </div>
                  </div>

                

                  {/* Assess Mode Persona */}
                  <div className={styles.card}>
                    <h4 className={styles.assessTitle}>
                      Assess Mode Character
                    </h4>
                    <div className={styles.fieldGroup}>
                      <div>
                        <label className={styles.label}>Role</label>
                        <input
                          type="text"
                          className={styles.input}
                          value={
                            templateData?.persona_definitions
                              ?.assess_mode_ai_bot?.role || ""
                          }
                          onChange={(e) =>
                            setTemplateData((prev) => ({
                              ...prev,
                              persona_definitions: {
                                ...prev.persona_definitions,
                                assess_mode_ai_bot: {
                                  ...prev.persona_definitions
                                    ?.assess_mode_ai_bot,
                                  role: e.target.value,
                                },
                              },
                            }))
                          }
                        />
                      </div>
                      <div>
                        <label className={styles.label}>Background</label>
                        <textarea
                          //   value={Persona?.assess_mode_ai_bot?.background || ""}
                          className={styles.textarea}
                          value={
                            templateData?.persona_definitions
                              ?.assess_mode_ai_bot?.background || ""
                          }
                          onChange={(e) =>
                            setTemplateData((prev) => ({
                              ...prev,
                              persona_definitions: {
                                ...prev.persona_definitions,
                                assess_mode_ai_bot: {
                                  ...prev.persona_definitions
                                    ?.assess_mode_ai_bot,
                                  background: e.target.value,
                                },
                              },
                            }))
                          }
                        />
                      </div>
                      <div>
                        <label className={styles.label}>
                          Behavioral Traits
                        </label>
                        <input
                          type="text"
                          value={
                            templateData?.persona_definitions
                              ?.assess_mode_ai_bot?.behavioral_traits || ""
                          }
                          onChange={(e) =>
                            setTemplateData((prev) => ({
                              ...prev,
                              persona_definitions: {
                                ...prev.persona_definitions,
                                assess_mode_ai_bot: {
                                  ...prev.persona_definitions
                                    ?.assess_mode_ai_bot,
                                  behavioral_traits: e.target.value,
                                },
                              },
                            }))
                          }
                          className={styles.input}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {selected === "Context" &&
                Object.entries(Context || {}).map(([key, value]) => (
                  <div className={styles.contentForm}>
                    <div className={styles.formTop}>
                      <div key={key}>
                        {key?.replace(/_/g, " ")?.replace(/\b\w/g, (char) => char?.toUpperCase())}
                      </div>
                      <input
                        type="text"
                        value={value}
                        onChange={(e) =>
                          setContext((prev) => ({
                            ...prev,
                            [key]: e.target.value,
                          }))
                        }
                        className={styles.input}
                      />
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
        <div className={styles.btnBox}>
              <div className={styles.cancelBtn} onClick={()=>{setSelectedData("showScenario",null),setCurrentPage()}}>Cancel</div>
              <div
                className={styles.saveBtn}
                onClick={() => {
                  handleSubmitData();
                }}
              >
                Save & Next
              </div>
              {/* <div
                className={styles.saveBtn}
                onClick={() => {
                  handleCreateAvatar();
                }}
              >
                Save & Add Avatar
              </div> */}
            </div>

      </div>
    </>
  );
}

export default EditDocument2;
