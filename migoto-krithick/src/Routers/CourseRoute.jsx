import React from 'react'
import { Route, Routes } from 'react-router-dom'
import CoursePage from '../Pages/CourseManagement/CoursePage'
import UplaodAction from '../Components/UplaodAction/UploadAction'
import ListofItems from '../Pages/ListofItems/ListofItems'
import CreateCourse from '../Pages/Course/CreateCourse'
import CreateModule from '../Pages/Course/CreateModule'
import CreateScenario from '../Pages/Course/CreateScenario'
import EditDocument from '../Pages/Course/AIScenario/EditDocument/EditDocument'
import DocumentUploadFlow from '../Pages/Course/DocUploadFlow/DocumentUploadFlow'
import AvatarSelection from '../Pages/AvatarSelection/AvatarSelection'
import LVESelection from '../Pages/Course/LVESelection/LVESelection'
import AIScenario from '../Pages/Course/AIScenario/AIScenario'
import AvatarCreation from '../Pages/AvatarCreation/AvatarCreation'
import PersonaPage from '../Pages/PersonaPage/PersonaPage'
import ModulePage from '../Pages/CourseManagement/ModulePage'
import ScenarioPage from '../Pages/CourseManagement/ScenarioPage'
import AvatarInteraction from '../Pages/CourseManagement/AvatarInteraction/AvatarInteraction'

function CourseRoute() {
  return (
    <>
        {/* --------------courseManagement-------------- */}
          <Routes>
             <Route path="courseManagement" element={<CoursePage />} />
             <Route path="courseManagement/showModule" element={<ModulePage />} />
             <Route path="courseManagement/showScenario" element={<ScenarioPage />} />
             <Route path="courseManagement/showAvatarInteraction" element={<AvatarInteraction />} />
             {/* <Route path="courseManagement/showAvatarInteraction" element={<CourseManagement />} />
             <Route path="courseManagement/showAvatarInteraction" element={<CourseManagement />} /> */}
            <Route path="courseManagement/createCourse" element={<CreateCourse />} />

            {/* CreateModule */}
            <Route path="courseManagement/createModule" element={<CreateModule />} />
            <Route path="courseManagement/showModule/createModule" element={<CreateModule />} />

            {/* CreateScenario */}
            <Route path="courseManagement/createScenario" element={<CreateScenario />} />
            <Route path="courseManagement/showModule/createScenario" element={<CreateScenario />} />
            <Route path="courseManagement/showScenario/createScenario" element={<CreateScenario />} />

            {/* EditDocument */}
            <Route path="courseManagement/createScenario/editContent" element={<EditDocument />} />
            <Route path="courseManagement/showModule/createScenario/editContent" element={<EditDocument />} />
            <Route path="courseManagement/showScenario/createScenario/editContent" element={<EditDocument />} />

            {/* DocumentUploadFlow */}
            <Route path="courseManagement/createScenario/videoPdf" element={<DocumentUploadFlow />} />
            <Route path="courseManagement/showModule/createScenario/videoPdf" element={<DocumentUploadFlow />} />
            <Route path="courseManagement/showScenario/createScenario/videoPdf" element={<DocumentUploadFlow />} />

            {/* AvatarCreation */}
            <Route path="courseManagement/createScenario/createAvatar" element={<AvatarCreation />} />
            <Route path="courseManagement/showModule/createScenario/createAvatar" element={<AvatarCreation />} />
            <Route path="courseManagement/showScenario/createScenario/createAvatar" element={<AvatarCreation />} />

            {/* PersonaPage */}
            <Route path="courseManagement/createScenario/personaCreation" element={<PersonaPage />} />
            <Route path="courseManagement/showModule/createScenario/personaCreation" element={<PersonaPage />} />
            <Route path="courseManagement/showScenario/createScenario/personaCreation" element={<PersonaPage />} />

            {/* AvatarSelection */}
            <Route path="courseManagement/createScenario/avatarSelection" element={<AvatarSelection />} />
            <Route path="courseManagement/showModule/createScenario/avatarSelection" element={<AvatarSelection />} />
            <Route path="courseManagement/showScenario/createScenario/avatarSelection" element={<AvatarSelection />} />

            {/* LVESelection */}
            <Route path="courseManagement/createScenario/Assign" element={<LVESelection />} />
            <Route path="courseManagement/showModule/createScenario/Assign" element={<LVESelection />} />
            <Route path="courseManagement/showScenario/createScenario/Assign" element={<LVESelection />} />

              </Routes>

    </>
  )
}

export default CourseRoute