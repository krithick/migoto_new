import React, { useEffect, useRef, useState } from "react";
import styles from "./CreateCourse.module.css";
import BulkIcon from "../../Icons/BulkIcon";
import TextArea from "antd/es/input/TextArea";
import { Button } from "antd";
import ReloadIcon from "../../Icons/ReloadIcon";
import axios from "../../service";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../store";
import { useNavigate } from "react-router-dom";
import { Navcontent } from "../Sidebar/SidebarPopUpContent.js";
import { UpdateTimeline } from "../../Components/Timeline/UpdateTImeLine.js";
import { getSessionStorage, setSessionStorage } from "../../sessionHelper.js";

function CreateModule({
  setCurrentPage,
  setData,
  data,
  currentPage,
  courseDetail,
}) {
  console.log('currentPage: ', currentPage);

  let flow = localStorage.getItem("flow");
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState();
  const { selectedData, setSelectedData } = useLOIData();
  const [preview, setPreview] = useState();
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    scenarios: [],
  });
  const { message, setMessage } = useUserPopupStore();
  const isFormValid =
    formData?.title.trim() !== "" && formData?.description.trim() !== "";
  const { isPreview, setIsPreview } = usePreviewStore();

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    if (!name) return;

    if (type !== "file") {
      setFormData((prevData) => ({
        ...prevData,
        [name]: value,
      }));
    }
  };

  const inputRef = useRef();

  const onSelectFile = (e) => {
    if (!e.target.files || e.target.files?.length === 0) {
      setSelectedFile(undefined);
      return;
    }

    setSelectedFile(e.target.files[0]);
  };

  useEffect(() => {
    if (!selectedFile) return;

    // ✅ Handle local File only
    if (typeof selectedFile === "object") {
      const objectUrl = URL.createObjectURL(selectedFile);
      setPreview(objectUrl);

      return () => URL.revokeObjectURL(objectUrl); // cleanup
    }
  }, [selectedFile]);

  useEffect(() => {
    if (flow == "CourseManagement flow" && getSessionStorage("showCourse")) {
      setSelectedData("courseId", getSessionStorage("showCourse"));
      sessionStorage.setItem("courseId", getSessionStorage("showCourse"));
    }
  }, []); //corseManagement flow creating module without creating course

  useEffect(() => {
    if (courseDetail) {
      setFormData({
        title: courseDetail.title ?? "",
        description: courseDetail.description ?? "",
        scenarios: courseDetail.scenarios ?? [],
      });
      setPreview(courseDetail.thumbnail_url);
      setSelectedFile(courseDetail.thumbnail_url);
    } else {
      setPreview(
        "https://meta.novactech.in:6445/uploads/image/20250813121337_193a25e1.jpg"
      );
      setSelectedFile(
        "https://meta.novactech.in:6445/uploads/image/20250813121337_193a25e1.jpg"
      );
    }
  }, [courseDetail]);

  const handleCreateCourseDetail = () => {
    let company_id = JSON.parse(localStorage.getItem("user"))?.company_id;
    if (flow == "CourseManagement & editModule flow") {
      axios
        .put(`/modules/${courseDetail.id}`, {
          company_id: company_id,
          ...formData,
        })
        .then((res) => {
          setMessage({
            enable: true,
            msg: "Module Edited Successfully",
            state: true,
          });
          setCurrentPage("showScenario");
          setSelectedData("showModule", null);
          localStorage.setItem("flow", "CourseManagement flow");
        })
        .catch((err) => {
          console.log("err: ", err);
          setMessage({
            enable: true,
            msg: "Something Went wrong",
            state: false,
          });
        });
    } else {
      let courseId = selectedData["courseId"]?selectedData["courseId"]:sessionStorage.getItem("courseId");
      axios
        .post(`/courses/${courseId}/modules`, {
          company_id: company_id,
          ...formData,
        })
        .then((res) => {
          // setData(res.data.id);
          setSelectedData("module id", res.data.id);
          setSelectedData("moduleId", res?.data?.id);
          setSessionStorage("moduleId",res?.data?.id)
          setMessage({
            enable: true,
            msg: "Module Created Successfully",
            state: true,
          });
          UpdateTimeline(2, {
            status: "success",
            description: `${res.data.title}`,
          },setSelectedData);
          UpdateTimeline(3, {
            status: "warning",
            description: `In Progress`,
          },setSelectedData);
          if (flow == "CourseManagement & editModule flow") {
            setCurrentPage("showModule");
            localStorage.setItem("flow", "CourseManagement flow");
          } else {
            // setCurrentPage("Create Scanario");
            const newPath = location.pathname.replace(
              "createModule",
              "createScenario"
            );
            navigate(newPath);
          }
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
  };

  const handleImageRequest = () => {
    // setCurrentPage("Create Scanario");
    if (typeof selectedFile === "object") {
      const token = localStorage.getItem("migoto-cms-token");

      const submissionData = new FormData();
      submissionData.append("file", selectedFile);
      submissionData.append("file_type", "image");

      axios
        .post("/uploads/", submissionData, {
          headers: {
            "Content-Type": "multipart/form-data",
            authorization: token,
          },
        })
        .then((res) => {
          console.log("Success:", res.data);
          formData["thumbnail_url"] = res.data?.live_url;
          setFormData(formData);
          handleCreateCourseDetail();
        })
        .catch((err) => {
          console.error("Submission error:", err);
        });
    } else {
      formData["thumbnail_url"] = selectedFile;
      setFormData(formData);
      handleCreateCourseDetail();
    }
  };

  const checkNavigation = () => {
    let result = new Promise((resolve) => {
      setIsPreview({
        enable: true,
        msg: `${
          Navcontent[window.location.pathname]
            ? Navcontent[window.location.pathname]
            : "Are you sure you want to proceed with this action?"
        }`,
        value: "ok/cancel",
        resolve,
      });
    });
    result.then((res) => {
      let path = window.location.pathname;
      if (res) {
        if(flow == "Create Course flow"){
          navigate(-1);
        }
        if (flow == "CourseManagement & editModule flow") {
          setCurrentPage("showScenario");
          // setSelectedData("showScenario", null);
          localStorage.setItem("flow", "CourseManagement flow");
        }else if(flow == "CourseManagement flow"){
          const cleanedPath = path?.replace("/createModule", "");
          navigate(cleanedPath);
          // navigate(-1,{travelTo:"showModule"})
          setSelectedData("showModule", null);
          // setSelectedData("showCourse", null);
          UpdateTimeline(2, {
            status: "error",
            description: ``
          },setSelectedData);
          UpdateTimeline(1, {
            status: "warning",
            description: `In Progress`
          },setSelectedData);
        }
        else{
          const cleanedPath = path?.replace("/createModule", "");
          navigate(cleanedPath);
          UpdateTimeline(2, {
            status: "error",
            description: ``
          },setSelectedData);
          UpdateTimeline(1, {
            status: "warning",
            description: `In Progress`
          },setSelectedData);

        }
      }
    });
  };

  return (
    <>
      <div className={styles.createCourseContainer}>
        <div className={styles.header}>
          <div className={styles.page}>
            <div className={styles.currentPage}>
              {flow == "CourseManagement & editModule flow"
                ? "Edit Module"
                : "Create Module"}
            </div>
          </div>
        </div>
        <div className={styles.formContainer}>
          <div className={styles.mainContainer}>
            <div className={styles.inputContainer}>
              <div className={styles.inputs}>
                <div className={styles.inputDiv}>
                  <label htmlFor="">
                    Module Title <span>*</span>
                  </label>
                  <input
                    name="title"
                    type="text"
                    className={styles.input}
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="Enter Module Title"
                  />
                </div>
                <div className={`${styles.inputDiv} `}>
                  <label htmlFor="">
                    Module Description <span>*</span>
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
                      id="file-upload"
                      type="file"
                      accept=".png, .jpg, .jpeg"
                      onChange={(e) => {
                        onSelectFile(e);
                      }}
                      style={{ display: "none" }}
                      ref={inputRef}
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
            <div className={styles.footer}>
              {
                <Button
                  className={styles.cancelBtn}
                  onClick={() => {
                    checkNavigation();
                  }}
                >
                  {"Cancel"}
                </Button>
              }
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

export default CreateModule;
