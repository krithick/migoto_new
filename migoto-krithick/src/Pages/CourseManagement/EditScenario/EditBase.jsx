
import React, { useRef, useState, useEffect } from "react";
import styles from "./EditBase.module.css";
import TextArea from "antd/es/input/TextArea";
import { Button, Input, Radio } from "antd";
import axios from "../../../service.js";
import { useLOIData, useUserPopupStore } from "../../../store";
import { useNavigate } from "react-router-dom";
import { BaseURL6445 } from "../../../helper";
import ReloadIcon from "../../../Icons/ReloadIcon.jsx";
import BulkIcon from "../../../Icons/BulkIcon.jsx";
import PdfIcon from "../../../Icons/PdfIcon.jsx";

function EditBase({setEditPage,courseDetail}) {
  let navigate = useNavigate();
  const { message, setMessage } = useUserPopupStore();

  let [visible, setVisible] = useState(false);
  let [pdfFile, setPdfFile] = useState(null);
  let [pdfFileData, setPdfFileData] = useState(null);
  let [imageFile, setImageFile] = useState();
  const [selectedImage, setSelectedImage] = useState();
  const [imagePreview, setImagePreview] = useState();
  const [selectedPDF, setSelectedPDF] = useState();
  const [docs, setDocs] = useState();
  const [loading, setLoading] = useState(false);
  let flow = localStorage.getItem("flow");
  const [pdfPreview] = useState("");
  let { selectedData, setSelectedData } = useLOIData();
  const [value, setValue] = useState(selectedData["Layout"]?selectedData["Layout"]:1);
  const [scenarioData, setScenarioData] = useState({
    title: "",
    description: "",
    thumbnail_url: ""
  });
  const imageInputRef = useRef();
  const pdfInputRef = useRef();

  const isFormValid =
    scenarioData?.title?.trim() !== "" &&
    scenarioData?.description?.trim() !== "" &&
    imagePreview 

    useEffect(()=>{
      if(courseDetail){
        setScenarioData({
          title: courseDetail.title,
          description:courseDetail.description,
          thumbnail_url:courseDetail.thumbnail_url
      })
      setSelectedImage(courseDetail.thumbnail_url)
      setImageFile(courseDetail.thumbnail_url)
      setImagePreview(courseDetail.thumbnail_url)
      }
    },[courseDetail])

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setScenarioData((prev) => ({
      ...prev,
      [name]: value,
    }));    
  };

  const handleImageUpload = (e) => {
    if (!e.target.files || e.target.files.length === 0) {
      setSelectedImage(undefined);
      return;
    }
    const file = e.target.files[0];
    setSelectedImage(file);
  }; //upload image

  useEffect(() => {
    if (!selectedImage) return;

    // ✅ Handle local File only
    if (typeof selectedImage === "object") {
      const objectUrl = URL.createObjectURL(selectedImage);
      setImagePreview(objectUrl);  
      return () => URL.revokeObjectURL(objectUrl); // cleanup
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
        imageFile = res.data.live_url;
        scenarioData["thumbnail_url"]=res.data.live_url;
        setScenarioData(scenarioData)
        handleSubmitDetails();
      })
      .catch((err) => {
        console.error("Upload failed:", err);
      });
    }else{
        scenarioData["thumbnail_url"]=imageFile;
        setScenarioData(scenarioData)
        handleSubmitDetails();
    }
  }; //uplaod image in server
  let submissionData = new FormData();

  const handleSubmitDetails = () => {
    if(flow == "CourseManagement & editScenario flow"){
        axios
        .put(`/scenarios/${courseDetail.id}`, { ...scenarioData })
        .then((res) => {
          setMessage({
            enable: true,
            msg: "Scenario Edited Successfully",
            state: true,
          });
          setEditPage();
            setSelectedData("showScenario",null)
            localStorage.setItem("flow", "CourseManagement flow");
        })
        .catch((err) => {
          setMessage({
            enable: true,
            msg: "Something went wrong",
            state: false,
          });
        });
  
    }
  };


  return (
    <>
      <div className={styles.formContainer}>
        <div className={styles.mainContainer}>
          {/* -------------------------------------------------- */}
          {/* Title, Description, and Image Upload */}
          {<>
          <div className={styles.header}>
            <div>Edit Base Details</div>
          </div>
          <div className={styles.inputContainer}>
            <div className={styles.inputs}>
              <div className={styles.inputDiv}>
                <label>
                  Scenario Title <span>*</span>
                </label>
                <Input
                  type="text"
                  name="title"
                  disabled={selectedPDF}
                  value={scenarioData.title}
                  className={styles.input}
                  placeholder="Enter Scenario Title"
                  onChange={handleInputChange}
                />
              </div>
              <div className={styles.inputDiv}>
                <label>
                  Scenario Description <span>*</span>
                </label>
                <TextArea
                  name="description"
                  disabled={selectedPDF}
                  value={scenarioData.description}
                  className={styles.input}
                  placeholder="Enter Description here"
                  onChange={handleInputChange}
                  // maxLength={10000}
                />
              </div>
            </div>

            {/* Image Upload */}
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
                    disabled={selectedPDF}
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
                {!imagePreview && (
                  <div className={styles.iconContainer}>
                    <BulkIcon />
                  </div>
                )}
                {!imagePreview && (
                  <h3 className={styles.title}>
                    Upload Cover Picture from files
                  </h3>
                )}
                {!imagePreview && (
                  <p className={styles.subtitle}>Drag and drop here</p>
                )}
              </div>
            </div>
          </div>
            </>
          }           

          {/* Footer Buttons */}
          <div className={styles.footer}>
            {<Button  // cancel for navigate
              className={styles.cancelBtn}
              onClick={() => {
                setEditPage(),
                setSelectedData("showScenario",null)
                localStorage.setItem("flow", "CourseManagement flow");
                  }}
            >
              {"Cancel"}
            </Button>}
            {<Button
              className={styles.primaryBtn}
              type="primary"
              disabled={!isFormValid}
              onClick={() => {
                handleSubmitImage()
              }}
            >
              {"Submit"}
            </Button>}
          </div>
        </div>
      </div>
    </>
  );
}

export default EditBase;
