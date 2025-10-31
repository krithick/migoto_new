import React, { useEffect, useRef, useState } from "react";
import { useLOIData, usePreviewStore } from "../../store";
import styles from "../AvatarSelection/AvatarSelection.module.css";
import SearchIcon from "../../Icons/SearchIcon";
import CreateCourseIcon from "../../Icons/CreateCourseIcon";
import AvatarCard from "../../Components/ModesComponent/AvatarCard";
import CreateAvatarIcon from "../../Icons/CreateAvatarIcon";
import SelectionCard from "../../Components/Card/SelectionCard";
import axios from '../../service'
import { useNavigate } from "react-router-dom";
import { setSessionStorage } from "../../sessionHelper";
import BackIcon from "../../Icons/BackIcon";


function AvatarSelection() {
  
  const {isPreview, setIsPreview} = usePreviewStore();
  let navigate = useNavigate();
  const { selectedData, setSelectedData } = useLOIData();
  let [activeCourse, setActiveCourse] = useState("all");
  let [currentPage, setCurrentPage] = useState("avatarSelection");
  let [datas, setDatas] = useState([]);
  let [data, setData] = useState(datas);
  const [search, setSearch] = useState("");
  let userEmpId = JSON.parse(localStorage.getItem("user"));

  useEffect(() => {
    getAvatarInteractions()
  }, []);

  const getAvatarInteractions = () => {

    axios
      // .get("/avatars/?skip=0&limit=1000")
      .post("/avatars/batch",{
        avatar_ids: JSON.parse(sessionStorage.getItem("ListOfAvatar"))
      })
      .then((res) => {
        const reversedData = res?.data
        setDatas(reversedData);
        // setDatas(selectedData["ListofAvatars"])
      })
      .catch((err) => {
        console.log("err: ", err);
      });

  }

  const handleChangeCourse = (filter) => {
    setActiveCourse(filter);
    if (filter === "all") {
      setData(datas); // Show all data
    } else if (filter === "Me") {
      setData(datas?.filter((item) => item?.created_by === userEmpId?.id));
    } else if (filter === "Predefined") {
      setData(datas?.filter((item) => item?.status === "Predefined"));
    } else {
      // For Super Admin / Admin
      setData(datas?.filter((item) => item?.creater_role === filter));
    }
  };
  

  const handleSubmit = () => {
    // setCurrentPage("LVESelection")
    let path = window.location.pathname;
    const cleanedPath = path?.replace("/avatarSelection", "/assign");
    navigate(cleanedPath)

    setSelectedData("Language",null)
    setSelectedData("Environment",null)
    setSelectedData("Voice",null)
    // setCurrentPage("listofitem")
  }

  const scrollRef = useRef(null);

  const handleNavigate = () => {
    setSelectedData("personaCreated",1)
    setSessionStorage("personaLimit",0)
    let path = window.location.pathname;
    const cleanedPath = path?.replace("/avatarSelection", "/personaCreation");
    navigate(cleanedPath)
    // navigate(-2);
  }

  useEffect(() => {
    setSessionStorage("avatarSelection",selectedData["avatarSelection"])
  }, [selectedData["avatarSelection"]]);


    useEffect(() => {
      if (search.trim() === "") {
        setData(datas);
      } else {
        const filtered = datas?.filter((item) =>
          item?.name?.toLowerCase()?.includes(search?.toLowerCase())
        );
        setData(filtered);
      }
    }, [search, datas]);

  return (
    <div className={styles.avatarContainer}>
      <div className={styles.avatarHeader1}>
        <div className={styles.avatarHeaderLeft}>
          <div className={styles.detail}>
            <BackIcon onClick={()=>{navigate(-2)}} />
            <p>Assign Avatar</p>
          </div>
        </div>
        <div className={styles.avatarHeaderRight}>
        {<div className={styles.searchBar}><input type="text" placeholder={`Search ...`} onChange={(e) => { setSearch(e.target.value) }} />
          <SearchIcon className={styles.searchIconSvg} /></div>}
          {<button onClick={()=>{
            handleNavigate()}}>
            Create Avatar
            <CreateAvatarIcon />
          </button>}
        </div>
      </div>

      {/* <div className={styles.avatarHeader2}>
        <div className={styles.avatarHeaderLeft}>
          <div className={styles.currentContent}>
            <div className={`${styles.activeHeader} ${currentPage=="CoachSelection" && styles.setActiveHeader}`}>
              <span> 01 </span> Avatar Selection
            </div>{" "}
            {" > "}
            <div className={`${currentPage=="CoachSelection" && styles.activeHeader}`}>
              <span> 02 </span> Coach AI Selection
            </div>
          </div>
        </div>
      </div> */}

      <div className={styles.avatarHeader3}>
        <div className={styles.avatarHeaderLeft}>
          <div className={styles.totalBox}>
            <div
              className={`${styles.box} ${
                activeCourse === "all" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("all");
              }}
            >
              All
            </div>
            <div
              className={`${styles.box} ${
                activeCourse === "Predefined" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("Predefined");
              }}
            >
              Pre - Defined Courses
            </div>
            <div
              className={`${styles.box} ${
                activeCourse === "Super Admin" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("Super Admin");
              }}
            >
              Created by Super Admin
            </div>
            <div
              className={`${styles.box} ${
                activeCourse === "Admin" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("Admin");
              }}
            >
              Created by Admin
            </div>
            <div
              className={`${styles.box} ${
                activeCourse === "Me" ? styles.active : ""
              }`}
              onClick={() => {
                handleChangeCourse("Me");
              }}
            >
              Created by Me
            </div>
          </div>
        </div>
      </div>
      {/* -------------------Body--------------- */}
      <div className={styles.loiBodyOuter} >
        <div className={styles.loiBody} ref={scrollRef}>
          {data?.map((item, index) => {
            return (
              <SelectionCard data={item} key={index} currentPage={currentPage} />
            );
          })}
        </div>
      </div>
      <div className={styles.BtnGroup}>
        {<button className={styles.cancelBtn} onClick={()=>{navigate(-1)}}>Cancel</button>}
        <button
          className={styles.nextBtn}
          disabled={!selectedData[currentPage]?.length > 0}
          onClick={()=>{handleSubmit()}}>
          Assign Details
        </button>
      </div>
    </div>
  );
}

export default AvatarSelection;
