import React, { useEffect, useRef, useState } from "react";
import styles from "../AIScenario/AiScenarioBuilder.module.css";
import BackIcon from "../../../Icons/BackIcon";
import AIicon from "../../../Icons/AIicon";
import LinkIcon from "../../../Icons/LinkIcon";
import { useNavigate } from "react-router-dom";
import axios from '../../../service'
import { useLOIData, useUserPopupStore } from "../../../store";
import ReloadIcon from "../../../Icons/ReloadIcon";
import BulkIcon from "../../../Icons/BulkIcon";
import Loader from "../../../Components/Loader/Loader";
import Radio from "antd/es/radio/radio";
import { BaseURL6445 } from "../../../helper";
import SupportDocUpload from "./SupportDocUpload/SupportDocUpload";
import { setSessionStorage } from "../../../sessionHelper";

function AiScenarioBuilder({ currentPage, setCurrentPage, setUploadPage }) {
  const { message, setMessage } = useUserPopupStore();
  const [selected, setSelected] = useState(1);
  let navigate = useNavigate();
    const {selectedData, setSelectedData} = useLOIData();
  const [selectedImage, setSelectedImage] = useState();
  const [imagePreview, setImagePreview] = useState();
  const imageInputRef = useRef();
  let [imageFile, setImageFile] = useState();
  const [loading, setLoading] = useState(false);
  const [value, setValue] = useState(selectedData["Layout"]?selectedData["Layout"]:1);

  let [formData, setFormData] = useState({
    title: "",
    description: "",
    points:"",
    thumbnail_url:""
  });

  const handleImageUpload = (e) => {
    if (!e.target.files || e.target.files?.length === 0) {
      setSelectedImage(undefined);
      return;
    }
    const file = e.target.files[0];
    setSelectedImage(file);
  }; //upload image

  useEffect(() => {
    setImagePreview("https://meta.novactech.in:6445/uploads/image/20250820044532_90f0c68e.jpg")
    setSelectedImage("https://meta.novactech.in:6445/uploads/image/20250820044532_90f0c68e.jpg")
  }, [])

  useEffect(() => {
    if (!selectedImage) return 

    if(typeof selectedImage === "object"){
      const objectUrl = URL.createObjectURL(selectedImage);
      setImagePreview(objectUrl);
  
      return () => URL.revokeObjectURL(objectUrl);
    }
  }, [selectedImage]); //preview link of uploaded image

  const handleSubmitImage = () => {
    const token = localStorage.getItem("migoto-cms-token");

    if (typeof selectedImage === "object") {
    const submissionData = new FormData();

    submissionData.append("file", selectedImage);
    submissionData.append("file_type", "image");

    axios
      .post("/uploads/", submissionData, {
        headers: {
          "Content-Type": "multipart/form-data",
          authorization: token,
        },
      })
      .then((res) => {
        // pdfFile = res.data.live_url;
        imageFile = res.data.live_url;
        formData["thumbnail_url"]= res.data.live_url;
        setFormData(formData);
        handleGenerate()
      })
      .catch((err) => {
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: false,
        });
});
    }else{
      // handleSubmitDetails(selectedImage)
      formData["thumbnail_url"] = selectedImage;
      setFormData(formData)
      handleGenerate()
    }
  }; //uplaod image in server


  const handleGenerate = async () => {  
    let submissionData = new FormData();
    // const data = {
    //   scenario_document: formData.description,
    // };    
    submissionData.append("scenario_document", formData.description);
    submissionData.append("template_name", formData.title);
    selectedData["supportDocs"]?.forEach((doc) => {
      submissionData.append("supporting_docs", doc);
    });
    setSelectedData("template_name", formData.title);
    setSelectedData("scenarioData", formData);
    setSessionStorage("scenarioData", formData)
    try {
      const res = await axios.post(`/scenario/analyze-scenario-enhanced`, submissionData,{headers: {"Content-Type": "multipart/form-data",},});
      // setSelectedData("templateResponse", res.data.template_data);
      setSelectedData("template_id",res?.data?.template_id)
      setSessionStorage("template_id",res?.data?.template_id)
      setSessionStorage("Layout",value)
      navigate("editContent")
      setUploadPage("DataEdition");
    } catch (err) {
      console.log("err: ", err);
      setLoading(false);
      setMessage({
        enable: true,
        msg: "Something Went Wrong",
        state: false,
      })
    }
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  function isValid(){
    if(imagePreview && formData.title && formData.description && value){
      return true 
    }else{
      return false
    }
  }

    return (
    <>
    {/* {loading && <Loader />} */}
      <div className={styles.mainBox}>
        <div className={styles.mainHeader}>
          <BackIcon
            onClick={() => {
              setUploadPage("Image Upload")

            }}
          />
          <p>Create Scenario with AI</p>
        </div>
        <div className={styles.mainSection1}>
          <div className={styles.sectionContent}>
            <div className={styles.contentHeader}>
              <div className={styles.contentHeading}>
                AI Driven Scenario Generation
              </div>
              <p>
                Let AI help you build amazing scenarios in minutes — smarter,
                faster, and effortlessly.
              </p>
            </div>

            <div className={styles.singleColumnBox}>
              <div>
                Scenario Title<sup>*</sup>
              </div>
              <input
                type="text"
                name="title"
                placeholder="Enter Scenario Title"
                value={formData.title}
                onChange={handleInputChange}
              />
            </div>
            <div className={styles.singleColumnLargeBox}>
              <div>
                Scenario Description <sup>*</sup>
              </div>
              {/* <input type="text" placeholder="Scenario Description" /> */}
              <textarea
                name="description"
                placeholder="Scenario Description"
                value={formData.description}
                onChange={handleInputChange}
              />
            </div>
            
            {<div className={styles.fRow}>
            <SupportDocUpload/>
          </div>}


            {/* <div className={styles.singleColumnLargeBox}>
              <div>
                Points to Follow
              </div>
              <textarea
                name="points"
                placeholder="Key Points"
                value={formData.points}
                onChange={handleInputChange}
              />
            </div> */}
            <div className={styles.singleColumnLargeBox1}>
            <div className={styles.imgContainer}>
              <div className={styles.fileContainer}>
                <label
                  htmlFor="image-upload"
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    height: "100%",
                    cursor: "pointer",
                    opacity: 0,
                    zIndex: 1,
                  }}
                >
                  <input
                    id="image-upload"
                    type="file"
                    accept=".png, .jpg, .jpeg"
                    style={{ display: "none" }}
                    onChange={handleImageUpload}
                    ref={imageInputRef}
                  />
                </label>
                {imagePreview && (
                  <>
                    <img
                      className={styles.previewImage}
                      src={imagePreview}
                      alt="Image Preview"
                    />
                    <button
                      className={styles.reloadIcon}
                      onClick={() => imageInputRef.current.click()}
                    >
                      Re-upload <ReloadIcon />
                    </button>
                  </>
                )}
                {!imagePreview &&<div className={styles.iconContainer}>
                  <BulkIcon />
                </div>}
                {!imagePreview &&<h3 className={styles.title}>
                  Upload Cover Picture from files
                </h3>}
                {!imagePreview &&<p className={styles.subtitle}>Drag and drop here</p>}
              </div>
            </div>

            <div className={styles.layoutSection}>
              Assign Layout
              <div className={styles.layoutContainer}>
                <div className={styles.leftSection}>
                  <Radio.Group
                    className={styles.radioGroup}
                    onChange={(e) => {setValue(e.target.value),setSelectedData("Layout",e.target.value)}}
                    value={value}
                  >
                    <Radio className={styles.radioBtn} value={1}>
                      Layout 01
                    </Radio>
                    <Radio className={styles.radioBtn} value={2}>
                      Layout 02
                    </Radio>
                    <Radio className={styles.radioBtn} value={3}>
                      Layout 03
                    </Radio>
                  </Radio.Group>
                </div>
                <div className={styles.rightSection}>
                {value==1&&<img src={"https://meta.novactech.in:6445/uploads/image/20250918094920_7e5fe4f2.png"} alt={`Layout ${value}`} />}
                {value==2&&<img src={"https://meta.novactech.in:6445/uploads/image/20250918094825_f8189d49.png"} alt={`Layout ${value}`} />}
                {value==3&&<img src={"https://meta.novactech.in:6445/uploads/image/20250918094700_0489f1a1.png"} alt={`Layout ${value}`} />}                </div>
              </div>
            </div>

            </div>

            {/* <div className={styles.generateBtn}>
              <div className={styles.aiIcon}>
                <AIicon />
              </div>
              <div
                className={styles.generateBtnSub}
                onClick={() => {
                    handleSubmitImage();
                }}
              >
                Generate
              </div>
            </div> */}

          </div>
        </div>
        <div className={styles.generateBtn}>
              <div className={styles.aiIcon}>
                <AIicon />
              </div>
              <div
                className={styles.generateBtnSub}
                onClick={() => {
                  isValid() && handleSubmitImage();
                }}
              >
                Generate
              </div>
            </div>


      </div>
    </>
  );
}


export default AiScenarioBuilder;
