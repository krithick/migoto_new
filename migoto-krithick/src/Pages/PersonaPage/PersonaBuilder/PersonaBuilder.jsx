import React, { useState } from 'react';
import styles from '../PersonaBuilder/PersonaBuilder.module.css';
import { useNavigate } from 'react-router-dom';
import BackIcon from '../../../Icons/BackIcon';
import axios from '../../../service'
import { useLOIData, useUserPopupStore } from '../../../store';
import Loader from '../../../Components/Loader/Loader';

function PersonaBuilder({ currentPage,setCurrentPage }) {
  const { selectedData, setSelectedData } = useLOIData();
    const { message, setMessage } = useUserPopupStore();
  
  const [formData, setFormData] = useState({
    persona_type: "",
    business_or_personal: "business",
    location: "",
    persona_description: "",
    gender: "male"
  });
  const [loading, setLoading] = useState(false);


  let navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const isFormValid = Object.values(formData).every((val) => val.trim() !== "");


  const handleGenerate = () => {
    setLoading(true);

    axios
      .post("/personas/generate", {...formData })
      .then((res) => {
        setLoading(false);
        setSelectedData("PersonaSelection",res.data.id)
        if(localStorage.getItem("flow")=="Create Avatar flow"){
          navigate("createAvatar")
        }else{
          navigate(-1);
        }
        setMessage({
          enable: true,
          msg: "Persona Generated Successfully",
          state: true,
        });
      })
      .catch((err) => {
        console.log("err: ", err);
        setLoading(false)
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: true,
        });

      });
  };

  return (
    <>
    {/* {loading && <Loader />} */}
    <div className={styles.mainBox}>
      <div className={styles.mainHeader}>
        <BackIcon onClick={()=>{setCurrentPage()}} />
        <p>Persona Creation</p>
      </div>

      <div className={styles.mainSection}>
        <div className={styles.sectionContent}>
          <div className={styles.contentHeader}>
            <div className={styles.contentHeading}>AI Persona Builder</div>
            <p>Manage persona traits, interaction style, and emotional tone - all in one place</p>
          </div>

          <div className={styles.singleColumnBox}>
            <div>Persona Type <sup>*</sup></div>
            <input
              type="text"
              name="persona_type"
              value={formData.persona_type}
              onChange={handleChange}
              placeholder="Enter Persona Type"
            />
          </div>

          <div className={styles.twoColumnBox}>
            <div>Gender <sup>*</sup></div>
            <div>Location <sup>*</sup></div>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="Enter Location"
            />
          </div>

          <div className={styles.singleColumnLargeBox}>
            <div>Persona Description <sup>*</sup></div>
            <textarea
              type="text"
              name="persona_description"
              value={formData.persona_description}
              onChange={handleChange}
              placeholder="Enter Description"
            />
          </div>
        <div className={styles.generateBtnBox}>
          <div className={styles.generateBtn} onClick={handleGenerate}>
            Generate
          </div>
          </div>
        </div>

       {/* {<div className={styles.btnBox}>
          <div className={styles.cancelBtn} onClick={()=>{setCurrentPage()}}>Cancel</div>
          <button
            className={styles.saveBtn}
            style={{
              backgroundColor: isFormValid ? "#007bff" : "#ccc",
              cursor: isFormValid ? "pointer" : "not-allowed"
            }}
            onClick={handleSubmit}
          >
            Save & Upload
          </button>
        </div>} */}
      </div>
    </div>
    </>
  );
}

export default PersonaBuilder;
