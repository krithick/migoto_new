import React, { useEffect, useState } from "react";
import styles from "./PersonaCreation.module.css";
import BackIcon from "../../../Icons/BackIcon";
import axios from "../../../service";
import AIgradientIcon from "../../../Icons/AIgradientIcon";
import { useNavigate } from "react-router-dom";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../../store";
import { UpdateTimeline } from "../../../Components/Timeline/UpdateTImeLine";
import { getSessionStorage, setSessionStorage } from "../../../sessionHelper";

function PersonaCreation({}) {
  const navigate = useNavigate();
  const { isPreview, setIsPreview } = usePreviewStore();
  const [count, setCount] = useState(getSessionStorage("personaLimit"));

  const { selectedData, setSelectedData } = useLOIData();
  const [formData, setFormData] = useState({
    name: "",
    persona_type: "",
    description: "",
    gender: "male",
    age: "",
    location: "",
    business_or_personal: "business",
  });
  
  const [showPersonaModal, setShowPersonaModal] = useState(false);
  const [templateData, setTemplateData] = useState(null);
  const [selectedPersonaIndex, setSelectedPersonaIndex] = useState(0);
  const [selectedGender, setSelectedGender] = useState("");
  const [customPrompt, setCustomPrompt] = useState("");

  const { message, setMessage } = useUserPopupStore();

  const handleSecondPersonaCreation = (data) => {
    const persona = data?.personas?.[0] || data;
    
    const location = typeof persona?.location === 'object' 
      ? `${persona?.location?.city || ''}, ${persona?.location?.state || ''}`.trim()
      : persona?.location || '';

    const detailCategories = persona?.detail_categories || {};
    const conversationRules = persona?.conversation_rules || {};
    
    const dynamicFormData = {
      name: persona?.name || '',
      persona_type: persona?.role || persona?.persona_type || '',
      description: persona?.description || '',
      gender: persona?.gender?.toLowerCase() || 'male',
      age: persona?.age || '',
      location: location,
      archetype: persona?.archetype || '',
      mode: persona?.mode || '',
      scenario_type: persona?.scenario_type || '',
      business_or_personal: "business",
    };

    Object.entries(detailCategories).forEach(([key, value]) => {
      dynamicFormData[key] = typeof value === 'object' ? JSON.stringify(value, null, 2) : value;
    });

    Object.entries(conversationRules).forEach(([key, value]) => {
      dynamicFormData[`conversation_${key}`] = typeof value === 'object' ? JSON.stringify(value, null, 2) : value;
    });

    setFormData(dynamicFormData);
  };

  const handleGeneratePersona = () => {
    const templateId = localStorage.getItem("template_id") || sessionStorage.getItem("template_id");
    const payload = {
      template_id: templateId,
      persona_type_index: selectedPersonaIndex,
      gender: selectedGender || null,
      custom_prompt: customPrompt || null,
    };

    axios
      .post("/scenario/personas/v2/generate-and-save", payload)
      .then((res) => {
        const persona = res.data.persona;
        setSelectedData("2ndPersonaData", persona);
        handleSecondPersonaCreation({ personas: [persona] });
        sessionStorage.setItem("regenerated_persona_id", res.data.persona_id);
        setSessionStorage("personaLimit", count+1);
        setCount((prev)=>prev+1);
        setShowPersonaModal(false);
      })
      .catch((err) => {
        console.log("err: ", err);
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: false,
        });
      });
  };

  useEffect(() => {
    const templateId = localStorage.getItem("template_id") || sessionStorage.getItem("template_id");
    axios.get(`/scenario/load-template-from-db/${templateId}`)
      .then((res) => {
        setTemplateData(res?.data?.template_data);
      })
      .catch((err) => console.error("Failed to load template:", err));

    const personaConfigStr = sessionStorage.getItem("persona_config");
    
    if (personaConfigStr) {
      try {
        const config = JSON.parse(personaConfigStr);
        sessionStorage.removeItem("persona_config");
        setSelectedPersonaIndex(config.persona_type_index || 0);
        setSelectedGender(config.gender || "");
        setCustomPrompt(config.custom_prompt || "");
        setShowPersonaModal(true);
        return;
      } catch (e) {
        console.error("Failed to parse persona config", e);
      }
    }
    
    const persona = selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character;
    if (persona) {
      handleSecondPersonaCreation({ personas: [persona] });
    } else {
      setShowPersonaModal(true);
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleBack = () => {
    let path = window.location.pathname;
    let cleanedPath;
    if (localStorage.getItem("flow") == "Create Avatar flow") {
      const cleanedPath = path?.replace("/personaCreation", "");
      navigate(cleanedPath, { state: { myData: "List Of Modules" } });
      UpdateTimeline("Scenario Selection", { status: "error", description: `` }, setSelectedData);
      UpdateTimeline("Module Selection",{ status: "warning", description: `In Progress` }, setSelectedData);
      UpdateTimeline(5,{ status: "error", description: `` },setSelectedData);
    } else {
      if(getSessionStorage("ListOfAvatar")&& getSessionStorage("ListOfAvatar")?.length>0){
        cleanedPath = path?.replace("/personaCreation", "/avatarSelection");
      }else{
        cleanedPath = -1
      }
      navigate(cleanedPath);
    }
  };

  const handleSubmit = () => {
    const regeneratedId = sessionStorage.getItem("regenerated_persona_id");
    const originalId = sessionStorage.getItem("try_assess_persona_id") || selectedData["try_assess_persona_id"];
    const existingPersonaId = regeneratedId || originalId;
    
    const payload = {
      persona_data: {
        ...formData,
        business_or_personal: "business",
        template_id: localStorage.getItem("template_id") || null,
        mode: "assess_mode"
      }
    };

    const endpoint = existingPersonaId 
      ? `/scenario/personas/v2/update/${existingPersonaId}`
      : "/scenario/personas/v2/save";

    const method = existingPersonaId ? axios.put : axios.post;

    method(endpoint, payload)
      .then((res) => {
        const personaId = res.data.persona_id || existingPersonaId;
        setSelectedData("personaName", formData.name);
        setSelectedData("PersonaSelection", personaId);
        setSessionStorage("personaName", formData.name);
        setSessionStorage("PersonaSelection", personaId);
        // Also save as try_assess_persona_id for LVESelection
        sessionStorage.setItem("try_assess_persona_id", personaId);
        sessionStorage.removeItem("regenerated_persona_id");
        
        UpdateTimeline(5, { status: "success", description: `${formData.name}` }, setSelectedData);
        UpdateTimeline(6, { status: "warning", description: `In Progress` }, setSelectedData);

        let path = window.location.pathname;
        const cleanedPath = path?.replace("personaCreation", "createAvatar");
        navigate(cleanedPath);
      })
      .catch((err) => {
        console.log("err: ", err);
        setMessage({
          enable: true,
          msg: err.response?.data?.detail || "Failed to save persona",
          state: false,
        });
      });
  };

  const formatFieldName = (key) => {
    return key.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  };

  const fixedFields = ['name', 'persona_type', 'gender', 'age', 'location', 'description', 'business_or_personal'];
  const dynamicFields = Object.keys(formData).filter(key => !fixedFields.includes(key));

  return (
    <>
      {showPersonaModal && templateData && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <h3>Configure Persona Generation</h3>
            
            {templateData.persona_types && templateData.persona_types.length > 1 && (
              <div className={styles.formSection}>
                <label className={styles.formLabel}>Select Persona Type</label>
                <div className={styles.personaOptions}>
                  {templateData.persona_types.map((persona, index) => (
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
            )}

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
              <button className={styles.cancelBtn} onClick={() => setShowPersonaModal(false)}>
                Cancel
              </button>
              <button className={styles.saveBtn} onClick={handleGeneratePersona}>
                Generate Persona
              </button>
            </div>
          </div>
        </div>
      )}

      <div className={styles.mainBox}>
        <div className={styles.headers}>
          <div className={styles.page}>
            <div className={styles.currentPage}>Create Scenario</div>
          </div>
        </div>
        <div className={styles.mainHeader}>
          <div className={styles.mainHeaderContent}>
            <BackIcon onClick={() => handleBack()} />
            <p>Persona Creation</p>
          </div>
          <button
            className={styles.createBtn}
            onClick={() => setShowPersonaModal(true)}
            disabled={!(count<2)}
          >
            <div><AIgradientIcon /></div>
            <p>Regenerate Persona</p>
          </button>
        </div>
        <div className={styles.mainSection}>
          <div className={styles.sectionContent}>
            <div className={styles.twoColumnBox1}>
              <div className={styles.alignItem}>
                <div>Gender <sup>*</sup></div>
                <select name="gender" value={formData.gender} onChange={handleChange}>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </select>
              </div>
              <div className={styles.alignItem}>
                <div>Persona Type <sup>*</sup></div>
                <input type="text" name="persona_type" value={formData.persona_type} onChange={handleChange} placeholder="Enter persona type" />
              </div>
            </div>

            <div className={styles.twoColumnBox1}>
              <div className={styles.alignItem}>
                <div>Name <sup>*</sup></div>
                <input type="text" name="name" value={formData.name} onChange={handleChange} placeholder="Enter name" />
              </div>
              <div className={styles.alignItem}>
                <div>Age <sup>*</sup></div>
                <input type="text" name="age" value={formData.age} onChange={handleChange} placeholder="Enter age" />
              </div>
            </div>

            <div className={styles.twoColumnBox1}>
              <div className={styles.alignItem}>
                <div>Location <sup>*</sup></div>
                <input type="text" name="location" value={formData.location} onChange={handleChange} placeholder="Enter location" />
              </div>
              {formData.archetype && (
                <div className={styles.alignItem}>
                  <div>Archetype</div>
                  <input type="text" name="archetype" value={formData.archetype} onChange={handleChange} placeholder="Archetype" />
                </div>
              )}
            </div>

            <div className={styles.singleColumnBox1}>
              <div>Description <sup>*</sup></div>
              <textarea name="description" value={formData.description} onChange={handleChange} placeholder="Enter description" />
            </div>

            {dynamicFields.map((key) => (
              <div key={key} className={styles.singleColumnBox1}>
                <div>{formatFieldName(key)}</div>
                <textarea
                  name={key}
                  value={formData[key] || ''}
                  onChange={handleChange}
                  placeholder={`Enter ${formatFieldName(key).toLowerCase()}`}
                  rows={typeof formData[key] === 'string' && formData[key].length > 100 ? 6 : 3}
                />
              </div>
            ))}
          </div>
        </div>
        <div className={styles.btnBox}>
          <div className={styles.cancelBtn} onClick={() => handleBack()}>
            Cancel
          </div>
          <div className={styles.saveBtn} onClick={() => handleSubmit()}>
            Save & Upload
          </div>
        </div>
      </div>
    </>
  );
}

export default PersonaCreation;
