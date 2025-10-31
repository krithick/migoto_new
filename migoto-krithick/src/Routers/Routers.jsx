import React, { useEffect } from "react";
import { Route, Routes, useNavigate } from "react-router-dom";
import Dashboard from "../Pages/Dashboard/Dashboard";
import PersonaPage from "../Pages/PersonaPage/PersonaPage";
import BulkListPreview from "../Components/UplaodAction/BulkListPreview/BulkListPreview";
import ListofItems from "../Pages/ListofItems/ListofItems";
import AvatarManagement from "../Pages/AvatarManagement/AvatarManagement";
import SceneCanvas from "../Pages/AvatarCreation/SceneCanvas";
import { UpdateTimeline } from "../Components/Timeline/UpdateTImeLine";
import { useLOIData } from "../store";
import { getSessionStorage } from "../sessionHelper";
import DashboardRoute from "./DashboardRoute";
import CourseRoute from "./CourseRoute";
import UserRoute from "./UserRoute";
import AdminRoute from "./AdminRoute";


function Routers() {
  const { selectedData, setSelectedData } = useLOIData();
  let path = window.location.pathname;
  useEffect(() => {
    if (path.endsWith("editContent")) {
      console.log("path1: ", path);
      UpdateTimeline(
        3,
        {
          status: "warning",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        4,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        5,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        6,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        7,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
    }
    if (path.endsWith("videoPdf")) {
      console.log("path2: ", path);
      UpdateTimeline(
        3,
        {
          status: "success",
          description: `Yet to complete`,
        },
        setSelectedData
      );
      UpdateTimeline(
        4,
        {
          status: "warning",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        5,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        6,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        7,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
    }
    if (path.endsWith("personaCreation")) {
      console.log("path3: ", path);
      UpdateTimeline(
        4,
        {
          status: "success",
          description: ``,
        },
        setSelectedData
      );
      UpdateTimeline(
        5,
        {
          status: "warning",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        6,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        7,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
    }
    if (path.endsWith("createAvatar")) {
      UpdateTimeline(
        5,
        {
          status: "success",
          description: getSessionStorage(""),
        },
        setSelectedData
      );
      UpdateTimeline(
        6,
        {
          status: "warning",
          description: `In Progress`,
        },
        setSelectedData
      );
      UpdateTimeline(
        7,
        {
          status: "error",
          description: `In Progress`,
        },
        setSelectedData
      );
    }
    if (path.endsWith("Assign")) {
      UpdateTimeline(
        6,
        {
          status: "success",
          description: ``,
        },
        setSelectedData
      );
      UpdateTimeline(
        7,
        {
          status: "warning",
          description: `In Progress`,
        },
        setSelectedData
      );
    }
  }, [window.location.pathname]);
  return (
    <>
      <DashboardRoute />
      <CourseRoute />
      <UserRoute />
      <AdminRoute />
      <Routes>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="avatarManagement" element={<AvatarManagement />} />
        <Route path="createAvatar/assignCourse" element={<ListofItems />} />
        <Route
          path="createAvatar/createAvatar/personaCreation"
          element={<PersonaPage />}
        />
        <Route path="bulkList" element={<BulkListPreview />} />
        <Route path="use" element={<SceneCanvas />} />
      </Routes>
    </>
  );
}

export default Routers;
