import React, { useEffect, useState } from "react";

import styles from "../User/UserManagement.module.css";
import axios from "../../service";
import SearchIcon from "../../Icons/SearchIcon";
import PlusIcon from "../../Icons/PlusIcon";
import DeleteIcon from "../../Icons/DeleteIcon";
import EditIcon from "../../Icons/EditIcon"
import { useNavigate } from "react-router-dom";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../store";
import { TimeLineRoute } from "../../RouteHelper/TimeLineRoute";
import { setSessionStorage } from "../../sessionHelper";

function UserManagement() {
  const [userFilter, setUserFilter] = useState("Overall");
  const {isPreview, setIsPreview} = usePreviewStore();
  const [data, setData] = useState([]);
  const [datas, setDatas] = useState([]);
  const {selectedData, setSelectedData} = useLOIData();
  let navigate = useNavigate();
  const [search, setSearch] = useState("");
    const { setMessage } = useUserPopupStore();


  const fetchUsers = async () => {
    try {
      const userList = await axios.get("/auth/users");
      setData(userList.data);
      setDatas(userList.data);
    } catch (e) {
      console.log("Unable to fetch users", e);
    }
  };

  useEffect(() => {
    let filtered = [...datas];
  
    // Apply username search filter
    if (search) {
      filtered = filtered?.filter((user) =>
        user.username?.toLowerCase()?.includes(search?.toLowerCase())
      );
    }
  
    // Apply Active/Inactive filter
    if (userFilter === "Active") {
      filtered = filtered.filter((user) => user.is_active === true);
    } else if (userFilter === "Inactive") {
      filtered = filtered.filter((user) => user.is_active === false);
    }
  
    setData(filtered);
  }, [search, userFilter]);
    
  useEffect(() => {
    fetchUsers();
    setSelectedData("assignedCourse",null)
    setSelectedData("sessions",null)
    setSelectedData("moduleLists",null)
    setSelectedData("moduleHeader",null)
    setSelectedData("scenarioHeader",null)
    setSelectedData("courseHeader",null)
    localStorage.setItem("currentPathLocation","User")
  
  }, []);

  function formatDate(dateString) {
    const date = new Date(dateString); // Parse the input date string into a Date object

    // Get the day, month, and year
    const day = String(date.getDate()).padStart(2, "0"); // Ensure two-digit day
    const month = String(date.getMonth() + 1).padStart(2, "0"); // Get month (1-based)
    const year = date.getFullYear(); // Get full 4-digit year

    // Return formatted date as "DD/MM/YYYY"
    return `${day}-${month}-${year}`;
  }

  const confirmPopup = (user) => {
    return new Promise((resolve) => {
      setIsPreview({
        enable: true,
        msg: [1],
        value: "deletePopUp",
        resolve,
      });
    });
  };
  
  const handleDelete = async (user) => {
    const confirmed = await confirmPopup(user);
    if (!confirmed) return;

      axios
      .delete(`/auth/users/${user.id}`)
      .then((res) => {
        setMessage({
          enable: true,
          msg: "User Deleted Successfully",
          state: true,
        });
        fetchUsers()
      })
      .catch((err) => {
        console.log("err: ", err);
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: false,
        });
      });
  }

  const handleUser  = async(_) => {
      try {
        const userList = await axios.get(`/auth/users/${_}`);
        setSessionStorage("userData", userList)
        navigate(`/migoto-cms/users/${_}/course`);
      } catch (e) {
        console.log("Unable to fetch users", e);
      }
  }

  return (
    <>
      <div className={styles.mainBox}>
        {/* header */}
        <div className={styles.mainHeader}>
          <div className={styles.mainHeaderLeft}>
            <p>User List</p>
            <div className={styles.buttonBox}>
              <div
                className={`${styles.overallBtn} ${
                  userFilter == "Overall" ? styles.selected : ""
                }`}
                onClick={() => {
                  setUserFilter("Overall");
                }}
              >
                <div>Overall</div>
                <div className={styles.btnValue}>
                  {datas.length > 0 ? datas.length : 0}
                </div>
              </div>
              <div
                className={`${styles.activeBtn} ${
                  userFilter == "Active" ? styles.selected : ""
                }`}
                onClick={() => {
                  setUserFilter("Active");
                }}
              >
                <div>Active</div>
                <div className={styles.btnValue}>
                  {datas.length > 0
                    ? datas.filter((x) => x.is_active === true).length
                    : 0}
                </div>
              </div>
              <div
                className={`${styles.inactiveBtn} ${
                  userFilter == "Inactive" ? styles.selected : ""
                }`}
                onClick={() => {
                  setUserFilter("Inactive");
                }}
              >
                <div>Inactive</div>
                <div className={styles.btnValue}>
                  {datas.length > 0
                    ? datas.filter((x) => x.is_active === false).length
                    : 0}
                </div>
              </div>
            </div>
          </div>
          <div className={styles.mainHeaderRight}>
            <div className={styles.addUserBtn} onClick={()=>{navigate("createUser"),localStorage.setItem("currentPathLocation","Create User"),
              localStorage.setItem("TLData",JSON.stringify(TimeLineRoute["/migoto-cms/users/createUser"]))}}>
              <div>
                <PlusIcon stroke={"white"} />
              </div>
              <div>Add User</div>
            </div>
            <div className={styles.searchBar}>
              <input type="text" placeholder="Search user..." onChange={(e)=>{setSearch(e.target.value)}} />
              <div>
                <SearchIcon />
              </div>
            </div>
          </div>
        </div>

        {/* Section */}
        <div className={styles.mainSection}>
          <div className={styles.sectionContent}>
            <table className={styles.userTable}>
              <thead className={styles.userThead}>
                <tr>
                  <th className={styles.userTh1}>S.no</th>
                  <th className={styles.userTh2}>Username</th>
                  <th className={styles.userTh3}>Employee Id</th>
                  <th className={styles.userTh4}>Email address</th>
                  {/* <th className={styles.userTh5}>Password</th> */}
                  <th className={styles.userTh6}>Created date</th>
                  <th className={styles.userTh7}>Course status</th>
                  <th className={styles.userTh8}>Status</th>
                  <th className={styles.userTh9}>Action</th>
                </tr>
              </thead>
              <tbody>
                {data.length > 0 &&
                  data.map((_, index) => (
                    <tr key={`row-${index + 1}`}>
                      <td className={styles.center}>{index + 1}</td>
                      <td>{_.username}</td>
                      <td>{_.emp_id}</td>
                      <td>{_.email}</td>
                      {/* <td>123456aaW</td> */}
                      <td>{formatDate(_.created_at)}</td>
                      <td id={`A${index + 1}`} className={`${_.assigned_courses.length > 0 ? styles.assigned : styles.notAssigned }`}>
                        {_.assigned_courses.length > 0
                          ? "Assigned"
                          : "Yet to assign"}
                      </td>

                      {/* Column 8 */}
                      <td className={styles.statusColumn}>
                        <div
                          className={`${styles.statusItem} ${
                            _.is_active
                              ? styles.statusItemGreen
                              : styles.statusItemRed
                          }`}
                          id={`S${index + 1}`}
                        >
                          <div className={styles.statusRound}>•</div>
                          <div className={styles.statusValue}>
                            {_.is_active ? "Active" : "Inactive"}
                          </div>
                        </div>
                      </td>

                      {/* Column 9 */}
                      <td>
                        <div className={styles.editColumn}>
                          <div
                            className={styles.editBox}
                            onClick={() => {
                              handleUser(_.id)
                              // navigate(`/migoto-cms/users/${_.id}`, {
                              //   state: { val: _},
                              // });
                            }}
                          >
                            <EditIcon/>
                          </div>
                          <div className={styles.deleteBox} onClick={()=>{handleDelete(_)}}><DeleteIcon/></div>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className={styles.mainFooter}></div>
      </div>
    </>
  );
}

export default UserManagement;
