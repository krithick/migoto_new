import React from "react";
import { Route, Routes } from "react-router-dom";
import AdminManagement from "../Pages/Admin/AdminManagement";
import CreateAdmin from "../Pages/Admin/CreateAdmin/CreateAdmin";
import EditAdmin from "../Pages/Admin/EditAdmin/EditAdmin";

function AdminRoute() {
  return (
    <>
      <Routes>
        <Route path="admins" element={<AdminManagement />} />
        <Route path="admins/createAdmin" element={<CreateAdmin />} />
        <Route path="admins/:id/editAdmin" element={<EditAdmin />} />
      </Routes>
    </>
  );
}

export default AdminRoute;