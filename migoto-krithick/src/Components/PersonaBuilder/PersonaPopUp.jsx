import React, { useEffect, useState } from 'react';
import styles from '../PersonaBuilder/PersonaPopUp.module.css';
import { useNavigate } from 'react-router-dom';
import axios from '../../service.js'
import { useLoaderStore, useLOIData, usePreviewStore, useUserPopupStore } from '../../store';
import BackIcon from '../../Icons/BackIcon.jsx';
import AIgradientIcon from '../../Icons/AIgradientIcon.jsx';
import { getSessionStorage, setSessionStorage } from '../../sessionHelper.js';

function PersonaPopUp() {
  const { selectedData, setSelectedData } = useLOIData();
  const {isPreview, setIsPreview} = usePreviewStore();
  const { message, setMessage } = useUserPopupStore();
  const loaderStore = useLoaderStore.getState();
  const [count, setCount] = useState(0);

  const [formData, setFormData] = useState({
    description: selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.description,
    background_story: selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.background_story,
    persona_details: selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.persona_details,
    persona_type: selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.persona_type,
    character_goal: selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.character_goal,
    gender: selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.gender?.toLowerCase(),
    name:selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.name,
    location:selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.location,
    age:selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.age,
    situation:selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.situation,
    context_type:selectedData["scenarioResponse"]?.generated_persona?.assess_mode_character?.context_type,
    business_or_personal:"business"
  });

  let navigate = useNavigate();
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));

    if(name == "gender"){
      GenerateByTemplateId(e.target.value);
    }
  };
//   const isFormValid = Object.values(formData).every((val) => val.trim() !== "");

  const handleGenerate = () => {
    axios
      .post("/personas/", {...formData })
      .then((res) => {
        setSelectedData("PersonaSelection",res.data.id)
        setSessionStorage("PersonaSelection",res.data.id)
        setSessionStorage("personaName",res.data.name)
        setSelectedData("personaName",res.data.name)
        setMessage({
          enable: true,
          msg: "Persona Created Successfully",
          state: true,
        });
        let increment = selectedData["personaCreated"]+1;
        setSelectedData("personaCreated",increment)
        if (isPreview.resolve) isPreview.resolve(true);
        setIsPreview({ enable: false, msg: "", value: "", resolve: null });
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

  const handleSecondPersonaCreation = (data) => {
    setFormData({
    description: data?.personas[0]?.description,
    background_story: data?.personas[0]?.background_story,
    persona_details: data?.personas[0]?.persona_details,
    persona_type: data?.personas[0]?.persona_type,
    character_goal: data?.personas[0]?.character_goal,
    gender: data?.personas[0]?.gender?.toLowerCase(),
    name:data?.personas[0]?.name,
    location:data?.personas[0]?.location,
    age:data?.personas[0]?.age,
    situation:data?.personas[0]?.situation,
    context_type:data?.personas[0]?.context_type,
    business_or_personal:"business"
    })
  }
  const GenerateByTemplateId =(value) => {
    if(value){
      let payload = {
        template_id: selectedData["template_id"],
        persona_type: "assess_mode_character",
        count: 1,
        gender:value,
        prompt:"",
      }

    axios
    .post("/generate-personas", { ...payload })
    .then((res) => {
      setSelectedData("2ndPersonaData", res.data);
      handleSecondPersonaCreation(res.data);
      setCount((prev)=>prev+1)
    })
    .catch((err) => {
      console.log("err: ", err);
      setMessage({
        enable: true,
        msg: "Something went wrong",
        state: false,
      });
    });
    return
    }
    if(selectedData["personaCreated"]==1){
      let payload = {
          template_id: getSessionStorage("template_id"),
          persona_type: "assess_mode_character",
          count: 1,
          gender:isPreview?.msg?.gender,
          prompt:isPreview?.msg?.promptText
        }

      axios
      .post("/generate-personas", {...payload })
      .then((res) => {
        setSelectedData("2ndPersonaData",res.data)
        handleSecondPersonaCreation(res.data)
        setCount((prev)=>prev+1)
      })
      .catch((err) => {
        console.log("err: ", err);
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: false,
        });
      });
  }

  }

  useEffect(()=>{
    GenerateByTemplateId()
  },[])

  const handleBack = () => {
    if (isPreview.resolve) isPreview.resolve(false);
    setIsPreview({ enable: false, msg: "", value: "", resolve: null });
  }
  const isFormValid = Object.values(formData).every((val) => val?.toString().trim() !== "");

  return (
    <>
    <div className={styles.backGround}>
    <div className={styles.mainBox}>
      <div className={styles.mainHeader}>
        <BackIcon onClick={()=>{handleBack()}} />
        <p>Recommended Persona</p>
      </div>

      <div className={styles.mainSection}>
        <div className={styles.sectionContent}>
          {/* <div className={styles.contentHeader}>
            <div className={styles.contentHeading}>Recommended Persona</div>
            <p>Manage persona traits, interaction style, and emotional tone - all in one place</p>
          </div> */}

            {/* Gender Persona type  */}
          <div className={styles.twoColumnBox1}>
            <div className={styles.alignItem}>
            <div>Gender <sup>*</sup></div>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              disabled={count > 2}
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
            </div>
            <div className={styles.alignItem}>
            <div>Persona Type <sup>*</sup></div>
            <input
              type="text"
              name="persona_type"
              value={formData.persona_type}
              onChange={handleChange}
              placeholder="Enter persona_type"
            />
            </div>
          </div>
          {/* Context Type Location */}
          <div className={styles.twoColumnBox1}>
            <div className={styles.alignItem}>
            <div>Context Type <sup>*</sup></div>
            <input
              type="text"
              name="context_type"
              value={formData.context_type}
              onChange={handleChange}
              placeholder="Enter context Type"
            />
            </div>
            <div className={styles.alignItem}>
            <div>Location <sup>*</sup></div>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="Enter location"
            />
            </div>
          </div>
          {/* Name Age */}
          <div className={styles.twoColumnBox1}>
            <div className={styles.alignItem}>
            <div>Name <sup>*</sup></div>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter name"
            />
          </div>
          <div className={styles.alignItem}>
          <div>Age <sup>*</sup></div>
          <input
              type="text"
              name="age"
              value={formData.age}
              onChange={handleChange}
              placeholder="Enter age"
            />
          </div>
          </div>

          {/* Background Story */}
          <div className={styles.singleColumnBox1}>
            <div>Background Story<sup>*</sup></div>
            <textarea
              type="text"
              name="background_story"
              value={formData.background_story}
              onChange={handleChange}
              placeholder="Enter background_story"
            />
          </div>
          {/* persona_details */}
          <div className={styles.singleColumnBox1}>
            <div>Persona Details <sup>*</sup></div>
            <textarea
              type="text"
              name="persona_details"
              value={formData.persona_details}
              onChange={handleChange}
              placeholder="Enter persona_details"
            />
          </div>
          {/* situation */}
          <div className={styles.singleColumnBox1}>
            <div>Situation <sup>*</sup></div>
            <textarea
              type="text"
              name="situation"
              value={formData.situation}
              onChange={handleChange}
              placeholder="Enter situation"
            />
          </div>
          {/* Description */}
          <div className={styles.singleColumnBox1}>
            <div>Description <sup>*</sup></div>
            <textarea
              type="text"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Enter description"
            />
          </div>
          {/* Goals */}
          <div className={styles.singleColumnBox1}>
            <div>Goal <sup>*</sup></div>
            <textarea
              type="text"
              name="character_goal"
              value={formData.character_goal}
              onChange={handleChange}
              placeholder="Enter character Goal"
            />
          </div>

          {/* <div className={styles.singleColumnLargeBox}>
            <div>Persona Description <sup>*</sup></div>
            <textarea
              type="text"
              name="persona_description"
              value={formData.persona_description}
              onChange={handleChange}
              placeholder="Enter Description"
            />
          </div> */}
        </div>
      </div>
      <div className={styles.generateBtnBox}>
      <button
          className={styles.createBtn}
          onClick={() => {
            GenerateByTemplateId();
          }}
          disabled={!(count<=2)}
        >
          {/* Replace with actual AI SVG */}
          <div>
            <AIgradientIcon />
          </div>
          <p>Regenerate Persona</p>
        </button>

          <div className={styles.generateBtn}   onClick={isFormValid ? handleGenerate : null}>
            Save & Use
          </div>
          </div>

    </div>
    </div>
    </>
  );
}

export default PersonaPopUp;
