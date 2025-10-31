import React, { useEffect, useState } from "react";
import styles from "../EditDocument/EditDocument.module.css";
import BackIcon from "../../../../Icons/BackIcon";
import AddIcon from "../../../../Icons/AddIcon";
import SectionCategoryPopup from "../../../User/SectionCategoryPopup/SectionCategoryPopup";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../../../store";
import { div } from "three/tsl";
import PlusIcon from "../../../../Icons/PlusIcon";
import axios from "../../../../service";
import Loader from "../../../../Components/Loader/Loader";
import { BaseURL6445 } from "../../../../helper";
import { Navcontent } from "../../../Sidebar/SidebarPopUpContent";
import { UpdateTimeline } from "../../../../Components/Timeline/UpdateTImeLine";
import { useNavigate } from "react-router-dom";
import { setSessionStorage } from "../../../../sessionHelper";
import AddPrompt from "./AddPrompt";
import DeleteIcon from "../../../../Icons/DeleteIcon";

function EditDocument({ setUploadPage }) {
  let [selected, setSelected] = useState("General Info");
  let { selectedData, setSelectedData } = useLOIData();
  const { message, setMessage } = useUserPopupStore();
  const { isPreview, setIsPreview } = usePreviewStore();
  let navigate = useNavigate()
  //for content section
  const [categoryStatus, setCategoryStatus] = useState(false);
  const [sectionStatus, setSectionStatus] = useState(false);
  const [templateData, setTemplateData] = useState();
  const [templateName, setTemplateName] = useState();
  const [sections, setSections] = useState([]);
  const [selectedPersonaIndex, setSelectedPersonaIndex] = useState(0);
  const [showPersonaSelector, setShowPersonaSelector] = useState(false);
  const [selectedGender, setSelectedGender] = useState("");
  const [customPrompt, setCustomPrompt] = useState("");
  let path = window.location.pathname;

  useEffect(()=>{
    axios
    .get(`/scenario/load-template-from-db/${sessionStorage.getItem("template_id")}`)
    .then((res) => {
      const data = res?.data?.template_data;
      setTemplateData(data);
      setTemplateName(res?.data?.name);
      
      // Dynamically build sections from template data
      const dynamicSections = Object.keys(data || {}).filter(key => 
        typeof data[key] === 'object' && data[key] !== null
      );
      setSections(dynamicSections);
      
      // Set first section as selected
      if (dynamicSections.length > 0) {
        setSelected(dynamicSections[0]);
      }
    })
    .catch((err) => {
      console.error("Submission error:", err);
    });
  },[])

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
        const response = await fetch(`${BaseURL6445}add-remove-points`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            section: section,
            subsection: subsection,
            action: "add",
            point_data: { content: result.trim() },
            current_template: templateData,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          setTemplateData(data.updated_template);
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
      const response = await fetch(`${BaseURL6445}add-remove-points`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          section: section,
          subsection: subsection,
          action: "remove",
          point_data: { index: index },
          current_template: templateData,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setTemplateData(data.updated_template);
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

  // Helper to format key to title
  const formatTitle = (key) => {
    return key?.replaceAll(/[_-]/g, " ")?.replace(/\b\w/g, (char) => char?.toUpperCase());
  };

  // Helper to check if value is array
  const isArrayField = (value) => Array.isArray(value);
  
  // Helper to check if value is object (but not array)
  const isObjectField = (value) => typeof value === 'object' && value !== null && !Array.isArray(value);
  
  // Helper to check if value is primitive
  const isPrimitiveField = (value) => typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean';

  const handleSubmitData = () => {
    handleSaveInDB(templateData, sessionStorage.getItem("template_id"), {
      persona_type_index: 0,
      gender: null,
      custom_prompt: null
    });
  };

  const handleSaveInDB = async (data, id, personaConfig) => {
    const payload = {
      template_data: data,
      template_name: templateName,
    };

    try {
      await axios.put(`${BaseURL6445}scenario/update-template-in-db/${id}`, payload);
      
      // Store persona config for PersonaCreation page to use
      sessionStorage.setItem("persona_config", JSON.stringify(personaConfig));
      
      const cleanedPath = path?.replace("editContent", "videoPdf");
      navigate(cleanedPath);
      setSelectedData("Document", []);
      setSelectedData("personaCreated", 0);
      setSelectedData("Video", []);
    } catch (err) {
      console.error("Failed to save:", err);
      setMessage({
        enable: true,
        msg: "Something Went Wrong",
        state: false,
      });
    }
  };
  

 
  const checkNavigation = () => {
    let result = new Promise((resolve) => {
      setIsPreview({
        enable: true,
            msg: `${Navcontent[window.location.pathname]?Navcontent[window.location.pathname]:"Are you sure you want to proceed with this action?"}`,
        value: "ok/cancel",
        resolve,
      });
    });
    result.then((res) => {
      if (res) {
          // setUploadPage("Image Upload"),
          const cleanedPath = path?.replace("/editContent", "");
          navigate(cleanedPath)
          setSelectedData("supportDocs", null),
          setSelectedData("scenarioData", null)
          // setSelectedData("scenarioResponse", null);
      }
    });
  };

  return (
    <>
      <AddPrompt />
      
      {/* Persona Type Selector Modal - Removed, now handled in PersonaCreation */}
      {false && showPersonaSelector && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <h3>Configure Persona Generation</h3>
            
            <div className={styles.formSection}>
              <label className={styles.formLabel}>Select Persona Type</label>
              <div className={styles.personaOptions}>
                {templateData?.persona_types?.map((persona, index) => (
                  <div
                    key={index}
                    className={`${styles.personaOption} ${selectedPersonaIndex === index ? styles.selectedOption : ''}`}
                    onClick={() => setSelectedPersonaIndex(index)}
                  >
                    <div className={styles.personaType}>{persona.type}</div>
                    <div className={styles.personaDesc}>{persona.description}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.formSection}>
              <label className={styles.formLabel}>Gender (Optional)</label>
              <select 
                className={styles.selectInput}
                value={selectedGender}
                onChange={(e) => setSelectedGender(e.target.value)}
              >
                <option value="">Auto-detect from template</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Non-binary">Non-binary</option>
              </select>
            </div>

            <div className={styles.formSection}>
              <label className={styles.formLabel}>Custom Instructions (Optional)</label>
              <textarea
                className={styles.textareaInput}
                placeholder="Add specific requirements for persona generation..."
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                rows={3}
              />
            </div>

            <div className={styles.modalButtons}>
              <button
                className={styles.cancelBtn}
                onClick={() => setShowPersonaSelector(false)}
              >
                Cancel
              </button>
              <button
                className={styles.saveBtn}
                onClick={() => {
                  setShowPersonaSelector(false);
                  handleSaveInDB(templateData, sessionStorage.getItem("template_id"), {
                    persona_type_index: selectedPersonaIndex,
                    gender: selectedGender || null,
                    custom_prompt: customPrompt || null
                  });
                }}
              >
                Save & Continue
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className={styles.mainBox}>
                {<div className={styles.header}>
                  <div className={styles.page}>
                    <div className={styles.currentPage}>Create Scenario</div>
                  </div>
                </div>}
      
        <div className={styles.mainHeader}>
          {/* <BackIcon /> */}
          <p>Edit Document</p>
        </div>
        <div className={styles.mainSection}>
          <div className={styles.sectionSidebar}>
            {sections.map((section) => (
              <div
                key={section}
                className={`${styles.unselected} ${selected === section ? styles.selected : ""}`}
                onClick={() => setSelected(section)}
              >
                {formatTitle(section)}
              </div>
            ))}
          </div>
          <div className={styles.sectionContent}>
            <div className={styles.contentHeader}>{formatTitle(selected)}</div>
            <div className={styles.sectionWrapper}>
              {templateData?.[selected] && (() => {
                const sectionData = templateData[selected];
                
                // Check if section has array fields (like knowledge_base with dos, donts, etc.)
                const arrayFields = Object.entries(sectionData).filter(([k, v]) => isArrayField(v));
                const objectFields = Object.entries(sectionData).filter(([k, v]) => isObjectField(v));
                const primitiveFields = Object.entries(sectionData).filter(([k, v]) => isPrimitiveField(v));
                
                // If section has array fields, render as cards with add/remove
                if (arrayFields.length > 0) {
                  return (
                    <div className={styles.container}>
                      {arrayFields.map(([key, items]) => (
                        <div key={key} className={styles.card}>
                          <div className={styles.header}>
                            <div>
                              <h4 className={styles.title}>{formatTitle(key)}</h4>
                            </div>
                            <button
                              onClick={() => handleAddPoint(selected, key)}
                              className={styles.addButton}>
                              <PlusIcon />
                              Add {formatTitle(key)}
                            </button>
                          </div>
                          <div className={styles.pointList}>
                            {items?.map((item, index) => (
                              <div key={index} className={styles.pointItem}>
                                <div className={styles.pointIndex}>{index + 1}</div>
                                <input
                                  type="text"
                                  value={typeof item === 'string' ? item : JSON.stringify(item)}
                                  onChange={(e) => handleEditPoint(selected, key, index, e.target.value)}
                                  className={styles.input}
                                />
                                <button
                                  onClick={() => handleRemovePoint(selected, key, index)}
                                  className={styles.removeButton}>
                                  <DeleteIcon />
                                </button>
                              </div>
                            ))}
                            {(!items || items.length === 0) && (
                              <div className={styles.emptyState}>
                                No {formatTitle(key).toLowerCase()} added yet. Click "Add {formatTitle(key)}" to get started.
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  );
                }
                
                // If section has nested objects, render recursively
                if (objectFields.length > 0 && primitiveFields.length === 0) {
                  return (
                    <div className={styles.container}>
                      {objectFields.map(([key, obj]) => (
                        <div key={key} className={styles.card}>
                          <h4 className={styles.title}>{formatTitle(key)}</h4>
                          <div className={styles.fieldGroup}>
                            {Object.entries(obj).map(([subKey, subValue]) => (
                              <div key={subKey} className={styles.contentForm}>
                                <div className={styles.formTop}>
                                  <label className={styles.label}>{formatTitle(subKey)}</label>
                                  {typeof subValue === 'string' && subValue.length > 100 ? (
                                    <textarea
                                      value={subValue}
                                      onChange={(e) => setTemplateData(prev => ({
                                        ...prev,
                                        [selected]: {
                                          ...prev[selected],
                                          [key]: {
                                            ...prev[selected][key],
                                            [subKey]: e.target.value
                                          }
                                        }
                                      }))}
                                      className={styles.textarea}
                                    />
                                  ) : (
                                    <input
                                      type="text"
                                      value={typeof subValue === 'object' ? JSON.stringify(subValue) : subValue}
                                      onChange={(e) => setTemplateData(prev => ({
                                        ...prev,
                                        [selected]: {
                                          ...prev[selected],
                                          [key]: {
                                            ...prev[selected][key],
                                            [subKey]: e.target.value
                                          }
                                        }
                                      }))}
                                      className={styles.input}
                                    />
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  );
                }
                
                // Default: render primitive fields as simple inputs
                return Object.entries(sectionData).map(([key, value]) => (
                  <div key={key} className={styles.contentForm}>
                    <div className={styles.formTop}>
                      <label className={styles.label}>{formatTitle(key)}</label>
                      {typeof value === 'string' && value.length > 100 ? (
                        <textarea
                          value={value}
                          onChange={(e) => setTemplateData(prev => ({
                            ...prev,
                            [selected]: {
                              ...prev[selected],
                              [key]: e.target.value
                            }
                          }))}
                          className={styles.textarea}
                        />
                      ) : (
                        <input
                          type="text"
                          value={typeof value === 'object' ? JSON.stringify(value) : value}
                          onChange={(e) => setTemplateData(prev => ({
                            ...prev,
                            [selected]: {
                              ...prev[selected],
                              [key]: e.target.value
                            }
                          }))}
                          className={styles.input}
                        />
                      )}
                    </div>
                  </div>
                ));
              })()}
            </div>
          </div>
        </div>

        <div className={styles.btnBox}>
              <div
                className={styles.cancelBtn}
                onClick={() => {
                  checkNavigation();
                }}
              >
                Cancel
              </div>
              <div
                className={styles.saveBtn}
                onClick={() => {
                  handleSubmitData();
                }}
              >
                Save & Upload
              </div>
          </div>

      </div>
    </>
  );
}

export default EditDocument;
