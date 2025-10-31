import React, { useState, useEffect, useRef, Suspense } from "react";
import { Grid, Html, Loader, useGLTF } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

import styles from "../AvatarCreation/AvatarCoustomization/AvtCustomiser.module.css";

//R3F components + svg components
import Character from "../AvatarCreation/AvatarCoustomization/Character";
import Chair from "../AvatarCreation/AvatarCoustomization/Chair";
import Lights from "../AvatarCreation/AvatarCoustomization/Lights";
import CameraController from "../AvatarCreation/AvatarCoustomization/CameraController";
import axios from "../../service";
import { Button, Input, Select } from "antd";
import { useLOIData, useUserPopupStore } from "../../store";
import { useNavigate } from "react-router-dom";
import IconSelection from "./AvatarCoustomization/IconSelection";
import { UpdateTimeline } from "../../Components/Timeline/UpdateTImeLine";
import { clearAllData, getSessionStorage, setSessionStorage } from "../../sessionHelper";
import { groupModelConfigsByName, transformModels } from "./AvatarCoustomization/avaterCreationHelper";

const chair = [{ id: "https://meta.novactech.in:6445/uploads/other/20250918095222_6168915a.glb" }];

function SceneCanvas({ setActiveState }) {
  const { selectedData, setSelectedData } = useLOIData();
  const [filter, setFilter] = useState("Body");
  const [ogConfig, setOgConfig] = useState([]);
  const [visibleByType, setVisibleBytype] = useState({});
  let [groupedModelConfigs, setGroupedModelConfigs] = useState([]);
  let [modelConfigs, setModelConfigs] = useState();
  let [isBeard, setIsBeard] = useState(false);
  let [Armature, setArmature] = useState();
  console.log('Armature: ', Armature);
  // let [path, setPath] = useState("/new mod/Joh_Armature.glb");
  const { message, setMessage } = useUserPopupStore();

  const [modelVisibility, setModelVisibility] = useState({});
  let [payloadName, setPayloadName] = useState(getSessionStorage("personaName"));
  let [gender, setGender] = useState("female");
  let [imageThumbnail, setImageThumbnail] = useState();
  let initialVisibility = {};
  let [payloadData, setPayloadData] = useState([]);
  let [payloadVisibility, setPayloadVisibility] = useState([]);
  let [payloadfbx, setPayloadfbx] = useState("");
  let visibleType = {};
  let person = ["Ama", "Da"];
  let file;
  let navigate = useNavigate();
  let flow = localStorage.getItem("flow");
  const [animationClips, setAnimationClips] = useState(null);
  const [play, setPlay] = useState(true);
  let path = window.location.pathname;

  // const handleBack = () => {
  //   if (flow != "Create Avatar flow") {
  //     const cleanedPath = path?.replace("/createAvatar", "/avatarSelection");
  //     navigate(cleanedPath, { state: { myData: "createAvatar" } });
  //   } else {
  //     const cleanedPath = path?.replace("createAvatar", "avatarSelection");
  //     navigate(cleanedPath);
  //     // navigate("assignCourse");
  //   }
  // };


  let canvasRef = useRef();

  const UploadImage = (file) => {
    const token = localStorage.getItem("migoto-cms-token");
    const submissionData = new FormData();

    submissionData.append("file", file);
    submissionData.append("file_type", "image");

    axios
      .post("/uploads/", submissionData, {
        headers: {
          "Content-Type": "multipart/form-data",
          authorization: token,
        },
      })
      .then((res) => {
        setImageThumbnail(res.data.live_url);
        PostAvatar(res.data.live_url);
      })
      .catch((err) => {
        console.error("Upload failed:", err);
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: false,
        });
      });
  };

  async function dataURLtoFile(dataUrl, filename) {
    const response = await fetch(dataUrl);
    const blob = await response.blob();
    return new File([blob], filename, { type: "image/png" });
  }

  let blob;
  const handleSubmit = async () => {
    const link = document.createElement("a");
    link.setAttribute("href", canvasRef.current.toDataURL("image/png"));

    link.setAttribute("download", "canvas-image.png"); // Specify the filename
    // link.click();   //for downloading that image
    link.remove();

    file = await dataURLtoFile(canvasRef.current.toDataURL("image/png"), "test.png");
    UploadImage(file);
  };

  // useEffect(()=>{
  //   const mode1 = selectedData["modifyAvaInterIn"];
  //   const idList = [
  //     {"LearnModeAvatarInteractionId":"LearnModeAvatar",
  //     "TryModeAvatarInteractionId":"TryModeAvatar",
  //     "AssessModeAvatarInteractionId":"AssessModeAvatar"},
  //   ];
  //   console.log('idList: ', selectedData[`${idList[0][mode1]}`]);
  // },[])

  const PostAvatar = (img) => {
    let payload = {
      name: payloadName,
      fbx: payloadfbx,
      animation: Armature[0]?.glb,
      glb: payloadData,
      selected: payloadVisibility,
      persona_id: [getSessionStorage("PersonaSelection")],
      gender: gender,
      thumbnail_url: img,
    };

    axios
      .post("/avatars/", { ...payload })
      .then((res) => {
        setMessage({
          enable: true,
          msg: "Avatar Created Successfully",
          state: true,
        });
        let existAvatar = JSON.parse(sessionStorage.getItem("ListOfAvatar") || "[]");
        if(!existAvatar.includes(res.data.id)){
          setSessionStorage("ListOfAvatar", [...(existAvatar || []), res.data.id]);
        }
        setSessionStorage("AvatarPreview", res.data.id);

        if (
          (flow == "CourseManagement & editScenario flow" && getSessionStorage("AvatarAssignedTo") == "all") || //this is for all interaction and edit scenario flow
          flow == "Create Avatar flow"
        ) {
          const idList = [
            { key: "LearnModeAvatarInteractionId", setKey: "LearnModeAvatar" },
            { key: "TryModeAvatarInteractionId", setKey: "TryModeAvatar" },
            { key: "AssessModeAvatarInteractionId", setKey: "AssessModeAvatar" },
          ];

          idList.map((v, i) => {
            let existing = getSessionStorage(v.setKey);
            axios
              .put(`/avatar-interactions/${getSessionStorage(v.key)}`, {
                avatars: [...existing, res.data.id],
              })
              .then((res) => {
                setSelectedData("checkAI", Date.now());
              })
              .catch((err) => {
                console.log(err);
                setMessage({
                  enable: true,
                  msg: "Something went wrong",
                  state: false,
                });
                return;
              });
          });
        } else if (flow == "CourseManagement & editScenario flow" && getSessionStorage("AvatarAssignedTo") == "single") {
          let mode = getSessionStorage("modifyAvaInterIn");
          const idList = [
            {
              LearnModeAvatarInteractionId: "LearnModeAvatar",
              TryModeAvatarInteractionId: "TryModeAvatar",
              AssessModeAvatarInteractionId: "AssessModeAvatar",
            },
          ];
          let existing = getSessionStorage(`${idList[0][mode]}`);

          axios
            .put(`/avatar-interactions/${getSessionStorage(`${mode}`)}`, {
              avatars: [...existing, res.data.id],
            })
            .then((res) => {
              setSelectedData("checkAI", Date.now());
            })
            .catch((err) => {
              console.log(err);
              setMessage({
                enable: true,
                msg: "Something went wrong",
                state: false,
              });
              return;
            });
        }

        setActiveState();
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
    const fetchModels = async () => {
      try {
        // Try to fetch both batches
        const requests = [
          axios.get("uploads/?file_type=model&skip=0&limit=100").catch(() => ({ data: [] })),
          axios.get("uploads/?file_type=model&skip=100").catch(() => ({ data: [] }))
        ];
        
        const [res1, res2] = await Promise.all(requests);
        const combinedData = [...(res1.data || []), ...(res2.data || [])];
        
        if (combinedData.length === 0) {
          console.warn("No model data received from API");
          setGroupedModelConfigs([]);
          return;
        }
        
        const overallData = groupModelConfigsByName(combinedData);
        setGroupedModelConfigs(transformModels(overallData));
      } catch (err) {
        console.error("Failed to fetch models:", err);
        setGroupedModelConfigs([]);
        setMessage({
          enable: true,
          msg: "Failed to load avatar models. Please refresh the page.",
          state: false,
        });
      }
    };
    
    fetchModels();
  }, []);

  useEffect(() => {
    if (groupedModelConfigs && groupedModelConfigs.length > 0) {
      setModelConfigs(groupedModelConfigs[0]?.models || []);
    } else {
      setModelConfigs([]);
    }
    setIsBeard(false);
  }, [groupedModelConfigs]);

  //group confign means data of all model data in array
  //model config means selected model data
  //ogConfig means single model data with visible key and without armature
  //config means single model data with visible key and without armature

  useEffect(() => {
    if (!modelConfigs || modelConfigs.length === 0) {
      setOgConfig([]);
      setPayloadVisibility([]);
      setPayloadData([]);
      setModelVisibility({});
      return;
    }

    const typeSeen = new Set();
    console.log('typeSeen: ', typeSeen);
    setArmature(modelConfigs?.filter((file) => file.fileName?.includes("Armature")) || []);

    const config = modelConfigs
      ?.filter((e) => e.fileName && !e.fileName?.toLowerCase()?.includes("armature"))
      ?.map((e) => {
        let file = e.fileName;
        let thumbnail = e.thumbnail;
        const parts = e.fileName?.replace(".glb", "")?.split("_");
        if (!parts || parts.length < 3) return null;
        
        const [Name, Type, ID] = parts;
        const isVisible = !typeSeen.has(Type);
        if (isVisible) typeSeen.add(Type);
        return {
          id: ID,
          type: Type,
          name: Name,
          visible: isVisible,
          url: e.glb,
          file: file,
          thumbnail: thumbnail,
        };
      })
      ?.filter(Boolean);

    setOgConfig(config);

    let newPayloadVisibility = [];
    let newPayloadData = [];

    config?.forEach((m) => {
      initialVisibility[m.id] = m.visible;

      if (m.visible) {
        visibleType[m.type] = m.file?.replace(".glb", "");

        newPayloadVisibility.push({
          category: m.type,
          file_name: visibleType[m.type],
        });
        newPayloadData.push({
          file: m.url,
          thumbnail: m.thumbnail,
          name: m.type,
        });
        payloadName = m.name;
        if (person?.includes(m.name)) {
          setGender("female");
        } else {
          setGender("male");
        }
      }
    });

    //visibleType and newPayloadVisibility both is same but structure is different

    // console.log("initialVisibility",initialVisibility);
    // console.log('visibleType: ', visibleType);
    // console.log('newPayloadVisibility: ', newPayloadVisibility);
    // console.log('newPayloadData: ', newPayloadData);

    if ("Beard" in visibleType) {
      setIsBeard(true);
    } else {
      setIsBeard(false);
    }

    setPayloadVisibility(newPayloadVisibility);
    setPayloadData(newPayloadData);
    setPayloadfbx(payloadName);
    setModelVisibility(initialVisibility);
    setVisibleBytype(visibleType);

  }, [modelConfigs]);

  const toggleModel = (id) => {
    console.log('id: ', id);
    const clickedModel = ogConfig.find((m) => m.id === id);
    const updated = { ...modelVisibility };

    if (clickedModel.type === "toggle") {
      updated[id] = !modelVisibility[id];
    } else {
      ogConfig.forEach((m) => {
        if (m.type === clickedModel.type) {
          if (clickedModel.type == "beard") {
            updated[m.id] = !modelVisibility[id];
          } else {
            updated[m.id] = m.id === id;
          }
        }
      });
    }

    const visibleType = {};
    const selectedPayload = [];
    const updatedPayloadData = [];
    Object.entries(updated).forEach(([modelId, isVisible]) => {
      const model = ogConfig.find((m) => m.id === modelId);
      if (isVisible && model) {
        visibleType[model.type] = model?.url?.replace(".glb", "");
        selectedPayload.push({
          category: model.type,
          file_name: model?.file?.replace(".glb", ""),
        });
        updatedPayloadData.push({
          file: model.url,
          thumbnail: model.thumbnail,
          name: model.type,
        });
      }
    });

    setVisibleBytype(visibleType);
    setModelVisibility(updated);
    setPayloadVisibility(selectedPayload);
    setPayloadData(updatedPayloadData);
  };

  return (
    <div className={styles.modelContainer}>
      <IconSelection
        setFilter={(item) => setFilter(item)}
        filter={filter}
        isBeard={isBeard}
        ogConfig={ogConfig}
        toggleModel={(item) => {
          toggleModel(item);
        }}
        setModelConfigs={(item) => setModelConfigs(item)}
        groupedModelConfigs={groupedModelConfigs}
      />
      {/* <div className={styles.fullSceneButton}>H</div> */}

      <div className={styles.sceneContainer}>
        <Canvas
          gl={{ preserveDrawingBuffer: true, logarithmicDepthBuffer: true }}
          onCreated={({ gl }) => {
            canvasRef.current = gl.domElement;
          }}
          camera={{ position: [0, 1, 2], fov: 45 }}
          shadows
        >
          <Lights />
          <Suspense
            fallback={
              <Html>
                <Loader
                  containerStyles={{
                    backgroundColor: "transparent",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                  innerStyles={{}} // optional custom styles
                  barStyles={{ backgroundColor: "#0085db" }} // change bar color
                  dataStyles={{ color: "#0085db" }} // change text color
                  dataInterpolation={(p) => `Loading ${p.toFixed(2)}%`}
                  initialState={(active) => active}
                />
              </Html>
            }
          >
            <Character
              modelConfigs={ogConfig}
              modelVisibility={modelVisibility}
              animationClips={animationClips}
              play={play}
            />
            <Chair chair={chair} />
          </Suspense>
          <OrbitControls enablePan={true} makeDefault />
          <CameraController filter={filter} />
        </Canvas>
      </div>
      <div className={styles.footer}>
        <div className={styles.container}>
          <Input
            placeholder="Character Name..."
            value={payloadName}
            onChange={(e) => {
              setPayloadName(e.target.value);
            }}
            readOnly
          ></Input>
          <Button
            type="primary"
            disabled={!payloadName || !ogConfig || ogConfig.length === 0}
            onClick={() => {
              if (ogConfig && ogConfig.length > 0) {
                setFilter(ogConfig[0]?.name || "Body");
                handleSubmit();
              }
            }}
          >
            Save
          </Button>
        </div>
      </div>
    </div>
  );
}

export default SceneCanvas;
