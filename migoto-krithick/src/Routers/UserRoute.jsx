import React from "react";
import { Route, Routes } from "react-router-dom";
import UserManagement from "../Pages/User/UserManagement";
import UplaodAction from "../Components/UplaodAction/UploadAction";
import CourseView from "../Pages/User/CourseView";
import ListofItems from "../Pages/ListofItems/ListofItems";
import UserCourse from "../Pages/User/UserDetails/UserCourse";
import UserModule from "../Pages/User/UserDetails/UserModule";
import UserScenario from "../Pages/User/UserDetails/UserScenario";
import UserChat from "../Pages/User/UserDetails/UserChat";
import EditUser from "../Pages/User/EditUser/EditUser";
import BulkListPreview from "../Components/UplaodAction/BulkListPreview/BulkListPreview";
import AssignBulkCourse from "../Pages/AssignCourse/AssignBulkCourse";

function UserRoute() {
  return (
    <>
      {/* --------------userManagement---------------- */}
      <Routes>
      <Route path="users" element={<UserManagement />} />
      <Route path="users/createUser" element={<UplaodAction />} />
      <Route path="users/createUser/bulkList" element={<BulkListPreview />} />
      <Route path="users/:id" element={<CourseView />} />
      <Route path="users/:id/assignCourse/:id" element={<ListofItems />} />
      <Route path="users/:id/course" element={<UserCourse />} />
      {/* <Route path="users/:id/course/assignCourse/:id" element={<AssignBulkCourse />} /> */}
      <Route path="users/:id/course/assignCourse/:id" element={<ListofItems />} />
      <Route path="users/:id/course/editUser" element={<EditUser />} />
      <Route path="users/:id/module" element={<UserModule />} />
      <Route path="users/:id/module/editUser" element={<EditUser />} />
      <Route path="users/:id/module/assignCourse/:id" element={<ListofItems />} />
      <Route path="users/:id/scenario" element={<UserScenario />} />
      <Route path="users/:id/scenario/editUser" element={<EditUser />} />
      <Route path="users/:id/scenario/assignCourse/:id" element={<ListofItems />} />
      <Route path="users/:id/chats" element={<UserChat />} />
      <Route path="users/:id/chats/editUser" element={<EditUser />} />
      </Routes>
    </>
  );
}

export default UserRoute;
