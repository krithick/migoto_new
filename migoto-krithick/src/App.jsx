import { useEffect, useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import Background from "./Pages/Background/Background";
import Sidebar from "./Pages/Sidebar/Sidebar";
import HeroPage from "./Pages/HeroPage/HeroPage";
import { usePreviewStore, useUserPopupStore } from "./store";
import AvatarPreview from "./Components/AvatarPreview/AvatarPreview";
import Message from "./Utils/Message/Message";
import Loader from "./Components/Loader/Loader";
import PersonaPopUp from "./Components/PersonaBuilder/PersonaPopUp";
import OkCancelPopUp from "./Components/PopUps/OkCancelPopUp";
import ALVEPopUp from "./Components/AssignALVEPopup/ALVEPopUp";
import UserSelect from "./Pages/User/UserSelect/UserSelect";
import PersonaPromptPopUp from "./Components/PopUps/PersonaPromptPopUp";
import MigotoLoader from "./Components/Loader/MigotoLoader";
import AILoader from "./Components/AILoader/AILoader";
import { useNavigate } from "react-router-dom";
import ConfirmationPopUp from "./Components/PopUps/ConfirmationPopUp";
import PersonaEditorPopUp from "./Components/PopUps/PersonaEditorPopUp";
// import '../src/local.js'
function App() {
  const {isPreview, setIsPreview} = usePreviewStore();
  const { message, setMessage } = useUserPopupStore();
  let navigate = useNavigate()


  return (
    <>
      <PersonaPromptPopUp />
      <ConfirmationPopUp />
      <ALVEPopUp />
      <OkCancelPopUp />
      {/* <AILoader /> */}
      <MigotoLoader />
      <Background />
      <Sidebar />
      <UserSelect />
      {isPreview.enable && isPreview.msg && isPreview.value=="AvatarPopUp"&&<PersonaEditorPopUp />}
      <div className="mainContainer">
      <HeroPage />
      </div>
      {/* {isPreview.enable && isPreview.msg && isPreview.value=="AvatarPopUp"&&
          <div className="PopUpContainer">
            <AvatarPreview />
            <div className="bgDark"></div>
            </div>
      } */}
      {isPreview.enable && isPreview.msg && isPreview.value=="PersonaPopUp"&&
          <div className="PopUpContainer">
            <PersonaPopUp />
            <div className="bgDark"></div>
            </div>
      }
      {message.enable &&  <Message />}

    </>
  );
}

export default App;
