// import React, { useEffect, useState } from 'react'
// import CreateCourse from './CreateCourse';
// import CreateModule from './CreateModule';
// import CreateScenario from './CreateScenario';
// import AvatarSelection from '../AvatarSelection/AvatarSelection';
// import { useLOIData } from '../../store';
// import LVESelection from './LVESelection/LVESelection';
// import ListofItems from '../ListofItems/ListofItems';
// import AiScenarioBuilder from './AIScenario/AiScenarioBuilder';
// import { useLocation, useNavigate } from 'react-router-dom';

// function Course() {

//     let [currentPage, setCurrentPage] = useState("Create Course");
//     let [data, setData] = useState();
//     const {selectedData, setSelectedData} = useLOIData();
//     const location = useLocation();
//     const navigate = useNavigate();
//     let flow = localStorage.getItem("flow");
//     let [moveTo, setMoveTo] = useState(false)
//     // let [isRefreshed,setIsRefreshed] = useState(false);

//     useEffect(()=>{
      //  if(location.state?.myData=="Document Upload"){
//         moveTo = true
//         setMoveTo(moveTo)
//         setCurrentPage("Create Scanario");

//        }else if(location.state?.myData=="createAvatar"){
//         setCurrentPage("avatarSelection");
//        }
//     },[location.state])

//   return (
//     <>
//       {currentPage=="Create Course" && <CreateCourse currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>}
//       {currentPage=="Create Module" && <CreateModule currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>}
//       {currentPage=="Create Scanario" && <CreateScenario currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}} moveTo={moveTo}/>}
//       {currentPage=="avatarSelection" && <AvatarSelection currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>}
//       {currentPage=="LVESelection" && <LVESelection currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>}
//       {currentPage=="listofitem" && <ListofItems currentPage={currentPage} setCurrentPage={(item)=>{setCurrentPage(item)}}/>}
//     </>
//   )
// }

// export default Course

// import React, { useEffect, useState } from 'react'
// import CreateCourse from './CreateCourse';
// import CreateModule from './CreateModule';
// import CreateScenario from './CreateScenario';
// import AvatarSelection from '../AvatarSelection/AvatarSelection';
// import { useLOIData } from '../../store';
// import LVESelection from './LVESelection/LVESelection';
// import ListofItems from '../ListofItems/ListofItems';
// import { useLocation, useNavigate } from 'react-router-dom';

// function Course() {

//     let [currentPage, setCurrentPage] = useState("Create Scanario");
//     let [data, setData] = useState();
//     const {selectedData, setSelectedData} = useLOIData();
//     const location = useLocation();
//     const navigate = useNavigate();
//     let flow = localStorage.getItem("flow");
//     let [moveTo, setMoveTo] = useState(false)

//     useEffect(()=>{
//        if(location.state?.myData=="Document Upload"){
//         moveTo = true
//         setMoveTo(moveTo)
//         setCurrentPage("Create Scanario");

//        }else if(location.state?.myData=="createAvatar"){
//         setCurrentPage("avatarSelection");
//        }
//     },[location.state])
    
//       useEffect(() => {
//         if (flow == "CourseManagement flow" && selectedData["showCourse"] && selectedData["showModule"]) {
//           setSelectedData("courseId", selectedData["showCourse"]);
//           setSelectedData("moduleId", selectedData["showModule"]);
//           sessionStorage.setItem("courseId", selectedData["showCourse"]);
//           sessionStorage.setItem("moduleId", selectedData["showModule"]);
//         }
//       }, []); //corseManagement flow creating module without creating course


//   return (
//     <>
//       {/* {currentPage=="Create Course" && <CreateCourse currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>} */}
//       {/* {currentPage=="Create Module" && <CreateModule currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>} */}
//       {currentPage=="Create Scanario" && <CreateScenario currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}} moveTo={moveTo}/>}
//       {currentPage=="avatarSelection" && <AvatarSelection currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>}
//       {currentPage=="LVESelection" && <LVESelection currentPage={currentPage} data={data} setCurrentPage={(item)=>{setCurrentPage(item)}} setData={(item)=>{setData(item)}}/>}
//       {currentPage=="listofitem" && <ListofItems currentPage={currentPage} setCurrentPage={(item)=>{setCurrentPage(item)}}/>}
//     </>
//   )
// }

// export default Course