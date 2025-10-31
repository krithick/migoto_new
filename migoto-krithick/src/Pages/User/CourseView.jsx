import React, { useEffect, useState } from 'react'
import CourseProgress from './CourseProgress/CourseProgress'
import CourseDetails from './CourseDetails/CourseDetails'
import { useLOIData } from '../../store';
import { useLocation, useParams } from 'react-router-dom';
import EditUser from './EditUser/EditUser';
import axios from '../../service.js'
function CourseView() {
  const {selectedData, setSelectedData} = useLOIData();
  const [currentPage, setCurrentPage] = useState("detailPage");
  const [data, setData] = useState();
  const location= useLocation();
 
  const fetchUsers = async () => {
    try {
      const userList = await axios.get(`/auth/users/${location.state.val.id}`);
      setData(userList.data);
    } catch (e) {
      console.log("Unable to fetch users", e);
    }
  };

  useEffect(() => {
    fetchUsers();
    localStorage.setItem("currentPathLocation","User")
  }, [currentPage,selectedData["assignedCourse"]]);

  return (
    <>
    {data && !selectedData["assignedCourse"] && currentPage=="detailPage"&&<CourseProgress val={data} Swap={()=>{setCurrentPage("editUser")}} />}
    {(data && selectedData["assignedCourse"]&& currentPage=="detailPage")&&<CourseDetails val={data} Swap={()=>{setCurrentPage("editUser")}} />}
    {data && currentPage == "editUser" && <EditUser val={data} Swap={()=>{setCurrentPage("detailPage")}}/>}
    </>
  )
}
  
export default CourseView