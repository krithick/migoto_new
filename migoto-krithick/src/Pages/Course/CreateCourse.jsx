import React, { useEffect, useRef, useState } from "react";
import styles from "./CreateCourse.module.css";
import BulkIcon from "../../Icons/BulkIcon";
import TextArea from "antd/es/input/TextArea";
import { Button } from "antd";
import ReloadIcon from "../../Icons/ReloadIcon";
import axios from "../../service";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../store";
import { useNavigate } from "react-router-dom";
import { Navcontent } from "../Sidebar/SidebarPopUpContent";
import { UpdateTimeline } from "../../Components/Timeline/UpdateTImeLine";
import { setSessionStorage } from "../../sessionHelper";

function CreateCourse({currentPage, setCurrentPage, setData, courseDetail }) {
  console.log('currentPage: ', currentPage);
  const { message, setMessage } = useUserPopupStore();
  let flow = localStorage.getItem("flow");
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState();
  const [preview, setPreview] = useState();
  let language = ["English", "Hindi"];
  let visibility = ["company_wide", "creator_only"];
  let [formData, setFormData] = useState({
    title: "",
    course_id: "",
    description: "",
    language: language[0],
    category: "",
    modules: [],
    visibility: visibility[0]
  });
  const { isPreview, setIsPreview } = usePreviewStore();
  let { selectedData, setSelectedData } = useLOIData();
  const isFormValid =
    formData?.title.trim() !== "" &&
    // formData?.course_id.trim() !== "" &&
    formData?.description.trim() !== "" 
    // formData?.category.trim() !== "";
  // formData?.language.trim() !== "";

  const inputRef = useRef();
  const onSelectFile = (e) => {
    if (!e.target.files || e.target.files?.length === 0) {
      setSelectedFile(undefined);
      return;
    }
    setSelectedFile(e.target.files[0]);
  };

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    // if (!name) return;

    if (type !== "file") {
      setFormData((prevData) => ({
        ...prevData,
        [name]: value,
      }));
    }
  };  

  useEffect(() => {
    // for Edit Course Data setting
    if (courseDetail) {
      setFormData({
        title: courseDetail.title ?? "",
        course_id: courseDetail.course_id ?? "",
        description: courseDetail.description ?? "",
        language: courseDetail.language ?? language[0],
        category: courseDetail.category ?? "",
        modules: courseDetail.modules ?? [],
        visibility: courseDetail.visibility?? visibility[0],
      });
      setPreview(courseDetail.thumbnail_url);
      setSelectedFile(courseDetail.thumbnail_url);
    }else{
      setPreview("https://meta.novactech.in:6445/uploads/image/20250813121042_20e7cb27.jpg")
      setSelectedFile("https://meta.novactech.in:6445/uploads/image/20250813121042_20e7cb27.jpg")
    }
  }, [courseDetail]);

  useEffect(() => {
    if (flow == "CourseManagement flow" && selectedData["showCourse"]) {
      // setData(selectedData["showCourse"]);
      setSelectedData("courseId", selectedData["showCourse"]);
    const newPath = location.pathname.replace("createCourse", "createModule");
    navigate(newPath);
    }
  }, []); //corseManagement flow creating module without creating course

  const handleCreateCourseDetail = () => {
    if (formData.course_id == "") {
      const randomCourseId = `${formData.title?.trim()?.charAt(0)?.toUpperCase() || "C"}${Math.floor(1000 + Math.random() * 9000)}`;
      formData["course_id"] = randomCourseId;
    }

    if(flow=="CourseManagement & editCourse flow"){ //put api
      axios
      .put(`/courses/${courseDetail.id}`, { ...formData })
      .then((res) => {
        setMessage({
          enable: true,
          msg: "Course Edited Successfully",
          state: true,
        });
          setCurrentPage("showModule");
          // setSelectedData("showCourse",null)
          localStorage.setItem("flow", "CourseManagement flow");
      })
      .catch((err) => {
        console.log("err: ", err);
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: false,
        });
      });
    }else{
      axios
      .post("/courses/", { ...formData })
      .then((res) => {
        // setData(res.data.id);
        setSelectedData("courseId", res?.data?.id);
        setSessionStorage("courseId", res?.data?.id);
        setMessage({
          enable: true,
          msg: "Course Created Successfully",
          state: true,
        });
        if (flow == "CourseManagement & editCourse flow") {
          setCurrentPage("showCourse");
          localStorage.setItem("flow", "CourseManagement flow");
        } else {
          // setCurrentPage("Create Module");
          const newPath = location.pathname.replace("createCourse", "createModule");
          navigate(newPath);
        }
        UpdateTimeline(1, {
          status: "success",
          description: `${res.data.title}`
        },setSelectedData);
        UpdateTimeline(2, {
          status: "warning",
          description: `In Progress`
        },setSelectedData);
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

  const handleImageRequest = () => {
    if (typeof selectedFile === "object") {
    const token = localStorage.getItem("migoto-cms-token");
    const submissionData = new FormData();
    // Append image file as binary
    submissionData.append("file", selectedFile); // Use binary file
    submissionData.append("file_type", "image"); // Optional: if required by backend

    axios
      .post("/uploads/", submissionData, {
        headers: {
          "Content-Type": "multipart/form-data", // Let browser set boundary
          authorization: token,
        },
      })
      .then((res) => {
        formData["thumbnail_url"] = res.data?.live_url;
        setFormData(formData);
        handleCreateCourseDetail();
      })
      .catch((err) => {
        console.error("Submission error:", err);
      });
    }else{
      formData["thumbnail_url"] = selectedFile;
      setFormData(formData)
      handleCreateCourseDetail();
    }
  };

  useEffect(() => {
    if (!selectedFile) return;

    if (typeof selectedFile === "object"){
      const objectUrl = URL.createObjectURL(selectedFile);
      setPreview(objectUrl);
  
      return () => URL.revokeObjectURL(objectUrl); // cleanup
    }
    }, [selectedFile]);


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
          if (flow == "CourseManagement & editCourse flow") {
            setCurrentPage("showModule"),
            setSelectedData("showCourse",null)
            localStorage.setItem("flow", "CourseManagement flow");
          } else {
            navigate(-1);
            UpdateTimeline(1, {
              status: "success",
              description: ``
            },setSelectedData);
            UpdateTimeline(2, {
              status: "warning",
              description: `In Progress`
            },setSelectedData);
          }}
      });
    };
  

  return (
    <>
      <div className={styles.createCourseContainer}>
        <div className={styles.header}>
          <div className={styles.page}>
            <div className={styles.currentPage}>{flow=="CourseManagement & editCourse flow"?"Edit Course":"Create Course"}</div>
          </div>
        </div>
        <div className={styles.formContainer}>
          <div className={styles.mainContainer}>
            <div className={styles.inputContainer}>
              <div className={styles.inputs}>
                <div className={styles.inputDiv}>
                  <label htmlFor="title">
                    Course Title <span>*</span>
                  </label>
                  <input
                    name="title"
                    type="text"
                    className={styles.input}
                    value={formData.title}
                    placeholder="Enter Course Title"
                    onChange={handleInputChange}
                  />
                </div>
                {/* <div className={styles.inputDiv}>
                  <label htmlFor="category">
                    Category <span>*</span>
                  </label>
                  <input
                    name="category"
                    type="text"
                    className={styles.input}
                    value={formData.category}
                    placeholder="Enter Category"
                    onChange={handleInputChange}
                  />
                </div> */}
                {/* <div className={styles.inputDiv}>
                  <label htmlFor="course_id">
                    Course Code / ID <span>*</span>
                  </label>
                  <input
                    name="course_id"
                    type="text"
                    value={formData.course_id}
                    className={styles.input}
                    placeholder="Enter CourseId"
                    onChange={handleInputChange}
                  />
                </div> */}
                <div className={styles.inputDiv}>
                  <label htmlFor="visiblity">
                   visibility <span>*</span>
                  </label>
                  <select
                    className={styles.input}
                    name="visibility"
                    value={formData.visibility}
                    onChange={handleInputChange}
                  >
                    {visibility.map((visible) => (
                      <option key={visible} value={visible}>
                        {visible}
                      </option>
                    ))}
                  </select>
                </div>
                <div className={styles.inputDiv}>
                  <label htmlFor="language">
                    Language <span>*</span>
                  </label>
                  <select
                    className={styles.input}
                    name="language"
                    value={formData.language}
                    onChange={handleInputChange}
                  >
                    {language.map((lang) => (
                      <option key={lang} value={lang}>
                        {lang}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className={styles.imgContainer}>
                <div className={styles.fileContainer}>
                  <label
                    htmlFor="file-upload"
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      width: "100%",
                      height: "100%",
                      cursor: "pointer",
                      opacity: 0,
                      zIndex: 1,
                      backgroundColor: "red",
                    }}
                  >
                    <input
                      ref={inputRef}
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      onChange={(e) => {
                        onSelectFile(e);
                      }}
                      accept=".png, .jpg, .jpeg"
                      style={{ display: "none" }}
                    />
                  </label>
                  {preview && (
                    <img className={styles.previewImage} src={preview} alt="" />
                  )}
                  {selectedFile && (
                    <button
                      className={styles.reloadIcon}
                      onClick={() => inputRef.current.click()}
                    >
                      {" "}
                      Re-upload <ReloadIcon />
                    </button>
                  )}
                  {!selectedFile && (
                    <div className={styles.iconContainer}>
                      {/* <ReactSVG src="/bulk.svg" /> */}
                      <BulkIcon />
                    </div>
                  )}
                  {!selectedFile && (
                    <h3 className={styles.title}>
                      Upload Cover Picture from files
                    </h3>
                  )}
                  {!selectedFile && (
                    <p className={styles.subtitle}>Drag and drop here</p>
                  )}
                </div>
              </div>
            </div>
            <div className={`${styles.inputDiv} ${styles.largerInput}`}>
              <label htmlFor="description">
                Course Description <span>*</span>
              </label>
              <TextArea
                name="description"
                type="text"
                className={styles.input}
                value={formData.description}
                placeholder="Enter Description here"
                onChange={handleInputChange}
              />
            </div>
            <div className={styles.footer}>
              <Button
                className={styles.cancelBtn}
                onClick={() => {
                  checkNavigation(window.location.pathname);
                }}
              >
                {"Cancel"}
              </Button>
              <Button
                disabled={!(preview && isFormValid)}
                className={styles.primaryBtn}
                type="primary"
                onClick={() => {
                  handleImageRequest()
                }}
              >
                {"Submit"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default CreateCourse;
