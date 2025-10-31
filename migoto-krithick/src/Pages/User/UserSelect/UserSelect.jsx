import React, { useEffect, useState } from "react";
import styles from "../UserManagement.module.css";
import axios from "../../../service";
import { useNavigate } from "react-router-dom";
import { Button } from "antd";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../../store";
import { setSessionStorage } from "../../../sessionHelper";

function UserSelect() {

  const [userFilter, setUserFilter] = useState("Overall");
  const [data, setData] = useState([]);
  const { selectedData, setSelectedData } = useLOIData();
  const [selectedUsers, setSelectedUsers] = useState([]); // State to track selected users
  let navigate = useNavigate();
  const [active, setActive] = useState();
  const { setUserPopup } = useUserPopupStore();
  const filteredData =
    userFilter === "Active"
      ? data.filter((user) => user.is_active === true)
      : userFilter === "Inactive"
      ? data.filter((user) => user.is_active === false)
      : data;

  const fetchUsers = async () => {
    try {
      const userList = await axios.get("/auth/users");
      setData(userList.data);
      console.log('userList.data: ', userList.data);
    } catch (e) {
      console.log("Unable to fetch users", e);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);



  // Function to handle checkbox toggle
  const handleCheckboxChange = (userId) => {
    setSelectedUsers(
      (prevSelected) =>
        prevSelected?.includes(userId)
          ? prevSelected.filter((id) => id !== userId) // Deselect
          : [...prevSelected, userId] // Select
    );
  };

  // useEffect(()=>{
    // setSelectedData("createdUser", selectedUsers)
    // setSessionStorage("createdUser", selectedUsers)
    // setSelectedData("createdUser", [])
  // },[selectedUsers])
  
  function formatDate(dateString) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    return `${day}-${month}-${year}`;
  }

    const { isPreview, setIsPreview } = usePreviewStore();
  
    if (isPreview.enable==false || isPreview.value !== "userListPopUp") return null;
  
    const handleCancel = () => {
      setSelectedData("createdUser", [])
      setSelectedUsers([])
      if (isPreview.resolve) isPreview.resolve(false);
      setIsPreview({ enable: false, msg: "", value: "", resolve: null });
    };

    const handleProceed = () => {
      if (isPreview.resolve) isPreview.resolve(selectedUsers);
      setIsPreview({ enable: false, msg: "", value: "", resolve: null});
    };
    

  return (
    <>
      <div className={styles.popupUser}>
        <div className={styles.overlay}>
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
                      {data.length > 0 ? data.length : 0}
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
                      {data.length > 0
                        ? data.filter((x) => x.is_active === true).length
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
                      {data.length > 0
                        ? data.filter((x) => x.is_active === false).length
                        : 0}
                    </div>
                  </div>
                </div>
              </div>
              <div className={styles.mainHeaderRight}>
                {/* <div className={styles.searchBar}>
                  <input type="text" placeholder="Search user..." />
                  <div>
                    <SearchIcon />
                  </div>
                </div> */}
              </div>
            </div>

            {/* Section */}
            <div className={styles.mainSection}>
              <div className={styles.sectionContent}>
                <table>
                  <thead className={styles.userThead}>
                    <tr>
                      <th className={styles.userTh0}>
                        {/* <input type="checkbox" /> */}
                      </th>
                      <th className={styles.userTh1}>S.no</th>
                      <th className={styles.userTh2}>Username</th>
                      <th className={styles.userTh3}>Employee Id</th>
                      <th className={styles.userTh4}>Email address</th>
                      <th className={styles.userTh6}>Created date</th>
                      <th className={styles.userTh7}>Course status</th>
                      <th className={styles.userTh8}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredData.length > 0 &&
                      filteredData.map((_, index) => (
                        <tr key={`row-${index + 1}`} onClick={()=>handleCheckboxChange(_.id)}>
                          <td className={styles.checkBox}>
                            <input
                              type="checkbox"
                              checked={selectedUsers?.includes(_.id)}
                              // onChange={() => handleCheckboxChange(_.id)}
                            />
                          </td>
                          <td>{index + 1}</td>
                          <td>{_.username}</td>
                          <td>{_.emp_id}</td>
                          <td>{_.email}</td>
                          <td>{formatDate(_.created_at)}</td>
                          <td id={`A${index + 1}`}>
                            {_.assigned_courses.length > 0
                              ? "Assigned"
                              : "Yet to assign"}
                          </td>
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
                          {/* <td>
                            <div className={styles.editColumn}>
                              <div
                                className={styles.editBox}
                                onClick={() => {
                                  navigate(`/migoto-cms/users/${_.id}`, {
                                    state: { val: _ },
                                  });
                                }}
                              >
                                E
                              </div>
                              <div className={styles.deleteBox}>D</div>
                            </div>
                          </td> */}
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className={styles.mainFooter}>
              <Button onClick={() => {handleCancel()}}>
                {" "}
                Cancel
              </Button>
              <Button
                type="primary"
                disabled={!selectedUsers?.length>0}
                onClick={() => {
                  // setSelectedData("createdUser", selectedUsers),
                  handleProceed()
                }}
              >
                {" "}
                Select Users
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default UserSelect;
