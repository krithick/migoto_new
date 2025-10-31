import React from 'react'
import { Route, Routes } from 'react-router-dom'
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
import ListofScenario from '../Components/ListofScenario/ListofScenario.jsx'
import BulkListPreview from '../Components/UplaodAction/BulkListPreview/BulkListPreview.jsx'
function DashboardRoute() {
  return (
    <>
    <Routes>
              <Route path="createUser" element={<UplaodAction />} />
              <Route path="createUser/bulkList" element={<BulkListPreview />} />
              <Route path="createUser/assignCourse" element={<ListofItems />} />
              <Route
                path="createUser/assignCourse/:id"
                element={<ListofItems />}
              />
              <Route
                path="createUser/assignCourse/:id/createCourse"
                element={<CreateCourse />}
              />
              <Route
                path="createUser/assignCourse/:id/createModule"
                element={<CreateModule />}
              />
              <Route
                path="createUser/assignCourse/:id/createScenario"
                element={<CreateScenario />}
              />
              <Route
                path="createUser/assignCourse/:id/createScenario/editContent"
                element={<EditDocument />}
              />
              <Route
                path="createUser/assignCourse/:id/createScenario/videoPdf"
                element={<DocumentUploadFlow />}
              />
              <Route
                path="createUser/assignCourse/:id/createScenario/avatarSelection"
                element={<AvatarSelection />}
              />
              <Route
                path="createUser/assignCourse/:id/createScenario/Assign"
                element={<LVESelection />}
              />
              <Route
                path="createUser/assignCourse/:id/createScenario/aiScenario"
                element={<AIScenario />}
              />
              <Route
                path="createUser/assignCourse/:id/createScenario/createAvatar"
                element={<AvatarCreation />}
              />
              <Route
                path="createUser/assignCourse/:id/createScenario/personaCreation"
                element={<PersonaPage />}
              />
              {/* --------------createCourse------------------ */}
              <Route path="createCourse" element={<CreateCourse />} />
              <Route path="createModule" element={<CreateModule />} />
              <Route path="createScenario" element={<CreateScenario />} />
              <Route
                path="createScenario/editContent"
                element={<EditDocument />}
              />
              <Route
                path="createScenario/videoPdf"
                element={<DocumentUploadFlow />}
              />
              <Route
                path="createScenario/personaCreation"
                element={<PersonaPage />}
              />
              <Route
                path="createScenario/createAvatar"
                element={<AvatarCreation />}
              />
              <Route
                path="createScenario/avatarSelection"
                element={<AvatarSelection />}
              />
              <Route
                path="createScenario/Assign"
                element={<LVESelection />}
              />

              {/* --------------createAvatar------------------ */}
              <Route path="selectScenario" element={<ListofScenario />} />
              <Route
                path="selectScenario/personaCreation"
                element={<PersonaPage />}
              />
              <Route
                path="selectScenario/createAvatar"
                element={<AvatarCreation />}
              />
            </Routes>
    </>
  )
}

export default DashboardRoute