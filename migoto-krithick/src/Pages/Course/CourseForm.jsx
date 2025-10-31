import React, { useRef, useState, useEffect } from "react";
import styles from "./CreateCourse.module.css";
import BulkIcon from "../../Icons/BulkIcon";
import TextArea from "antd/es/input/TextArea";
import { Button, Input, Radio } from "antd";
import ReloadIcon from "../../Icons/ReloadIcon";
import axios from "../../service";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../store";
import { useNavigate } from "react-router-dom";
import PdfIcon from "../../Icons/PdfIcon";
import SupportDocUpload from "./AIScenario/SupportDocUpload/SupportDocUpload";
import { BaseURL6445 } from "../../helper";
import { Navcontent } from "../Sidebar/SidebarPopUpContent";
import { UpdateTimeline } from "../../Components/Timeline/UpdateTImeLine";
import { setSessionStorage } from "../../sessionHelper";

function CourseForm({ setUploadPage, setCurrentPage }) {
  let navigate = useNavigate();
  const { message, setMessage } = useUserPopupStore();
  let path = window.location.pathname;
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
    layout: value,
  });
  const imageInputRef = useRef();
  const pdfInputRef = useRef();

  const isFormValid =
    scenarioData?.title?.trim() !== "" &&
    scenarioData?.description?.trim() !== "" &&
    imagePreview

    // useEffect(()=>{
    //   if(selectedData["Layout"]){
    //     setSessionStorage("Layout",selectedData["Layout"])
    //   }
    // },[selectedData["Layout"],value])


  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setScenarioData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

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
    // setUploadPage();
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
        handleSubmitDetails(imageFile);
      })
      .catch((err) => {
        console.error("Upload failed:", err);
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: false,
        });
      });
    }else{
      handleSubmitDetails(selectedImage)
    }
  }; //uplaod image in server

  // const handleSaveInDB = async (data,id) => {
  //   const payload = {
  //     template_data: data,
  //     template_name: pdfFile,
  //   };

  //   try {
  //     const res = await axios.put(
  //       `${BaseURL6445}update-template-in-db/${id}`,
  //       payload,
  //     );
  //   } catch (err) {
  //     console.error("Failed to save:", err);
  //     setMessage({
  //       enable: true,
  //       msg: "Something Went Wrong",
  //       state: true,
  //     })

  //   }
  // };
  


  let submissionData = new FormData();
  const handleSubmitDocs = async (e)=>{
    const token = localStorage.getItem("migoto-cms-token");

    submissionData.append("template_file", pdfFileData);

    selectedData["supportDocs"]?.forEach((doc) => {
      submissionData.append("supporting_docs", doc);
    });

    submissionData.append("template_name", pdfFile);

    try {
      setLoading(true);
      const res = await axios.post(
        `${BaseURL6445}scenario/analyze-template-with-optional-docs`,
        submissionData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            authorization: token,
          },
        }
      );
      setSelectedData("template_id",res?.data?.template_id);
      setSessionStorage("template_id",res?.data?.template_id);
      setScenarioData((prev) => ({
        ...prev,
        ["title"]: res.data?.template_data?.context_overview?.scenario_title,
        ["description"]: res.data?.template_data?.context_overview?.purpose_of_scenario,
      }));
      // setSelectedData("templateResponse", res.data?.template_data);
      setSelectedData("supportDocs",null)
      // handleSaveInDB(res.data?.template_data,res?.data?.template_id)
      setLoading(false);
      setVisible(!visible)
    } catch (err) {
      setLoading(false);
      console.error("Upload failed:", err);
      setMessage({
        enable: true,
        msg: "Something Went Wrong",
        state: false,
      })
    }
  }

  const handlePDFUpload =(e) => {
    if(e.target.files){
      setPdfFile(e.target.files[0]?.name)
      setPdfFileData(e.target.files[0])
      setSelectedData("template_name",(e.target?.files[0]?.name))
    }else{
      setPdfFile(null)
      setPdfFileData(null)
    }
  };

  const handleSubmitDetails = (img) => {
    let payload = { ...scenarioData, thumbnail_url: img };
    setSelectedData("scenarioData", payload);
    setSessionStorage("scenarioData", payload)
    setSessionStorage("Layout",value)
    // setUploadPage("DataEdition");
    navigate("editContent")

  };

  const { isPreview, setIsPreview } = usePreviewStore();

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
              flow == "CourseManagement flow" &&
                setSelectedData("showModule", null),
                setSelectedData("moduleId", null);
                setSelectedData("showCourse", null),
                setSelectedData("courseId", null);
                const cleanedPath = path?.replace("/createScenario", "");
                navigate(cleanedPath)
                }
            });
        };
  

  return (
    <>
      {/* {loading && <Loader />} */}
      <div className={styles.formContainer}>
        <div className={styles.mainContainer}>
          {/* PDF Upload Section */}
          {!visible && <div className={`${styles.inputDiv} ${styles.largerInput}`}>
            <label>
              Base Document <span>*</span>
            </label>
            <div className={styles.uploadContainer}
              onDragOver={(e) => {
                e.preventDefault();
                e.stopPropagation();
              }}
              onDrop={(e) => {
                e.preventDefault();
                e.stopPropagation();
                if (e.dataTransfer.files && e.dataTransfer.files?.length > 0) {
                  handlePDFUpload({ target: { files: e.dataTransfer.files } });
                  e.dataTransfer.clearData();
                }
              }}
            >
              <div className={styles.fileContainer}>
                <label
                  htmlFor="pdf-upload"
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
                    id="pdf-upload"
                    type="file"
                    accept=".pdf, .doc, .docx"
                    style={{ display: "none" }}
                    onChange={handlePDFUpload}
                    ref={pdfInputRef}
                  />
                </label>
                {pdfFile && (
                  <>
                    <PdfIcon />
                    <button
                      className={styles.reloadIcon}
                      onClick={() => pdfInputRef.current.click()}
                    >
                      Re-upload <ReloadIcon />
                    </button>
                  </>
                )}
                {!pdfFile && (
                  <div className={styles.iconContainer}>{<BulkIcon />}</div>
                )}
                <h3 className={styles.title}>
                  {pdfFile ? pdfFile : "Upload Document from files"}
                </h3>
                {!pdfFile && (
                  <p className={styles.subtitle}>Drag and drop here</p>
                )}
              </div>
            </div>
          </div>}

          {/* -------------------------------------------------- */}
          {/* Title, Description, and Image Upload */}
          {visible &&  <>   <div className={styles.inputContainer}>
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
          {/* Layout Selection */}
            <div className={styles.layoutSection}>
              Assign Layout
              <div className={styles.layoutContainer}>
                <div className={styles.leftSection}>
                  <Radio.Group
                    className={styles.radioGroup}
                    onChange={(e) => {setValue(e.target.value),setSelectedData("Layout",e.target.value)}}
                    value={value}>
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
                {value==3&&<img src={"https://meta.novactech.in:6445/uploads/image/20250918094700_0489f1a1.png"} alt={`Layout ${value}`} />}
                </div>
              </div>
            </div>
            </>
          }
          {/* ----------------------------------------------------   */}
          {/* Support Doc Upload */}
          {!visible && <div className={styles.fRow}>
            <SupportDocUpload/>
          </div>}
           

          {/* Footer Buttons */}
          <div className={styles.footer}>
            {!visible && <Button  // cancel for navigate
              className={styles.cancelBtn}
              onClick={() => {
                checkNavigation()
              }}
            >
              {"Cancel"}
            </Button>}
            {/* {visible&& <Button //cancel for visible
              className={styles.cancelBtn}
              onClick={() => {
                setVisible(!visible)
              }}
            >
              {"Cancel"}
            </Button>} */}
            {visible && <Button
              className={styles.primaryBtn}
              type="primary"
              disabled={!isFormValid}
              onClick={() => {
                handleSubmitImage()
              }}
            >
              {"Submit"}
            </Button>}
            {!visible&&<Button
              className={styles.primaryBtn}
              type="primary"
              disabled={!(pdfFile)}
              onClick={() => {
                handleSubmitDocs()
              }}
            >
              {"Next"}
            </Button>}
          </div>
        </div>
      </div>
    </>
  );
}

export default CourseForm;
