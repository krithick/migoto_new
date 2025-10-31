import React, { useEffect, useState } from "react";

import styles from "./AdminManagement.module.css";
import axios from "../../service";
import SearchIcon from "../../Icons/SearchIcon";
import PlusIcon from "../../Icons/PlusIcon";
import DeleteIcon from "../../Icons/DeleteIcon";
import EditIcon from "../../Icons/EditIcon"
import { useNavigate } from "react-router-dom";
import { useLOIData, usePreviewStore, useUserPopupStore } from "../../store";
import { TimeLineRoute } from "../../RouteHelper/TimeLineRoute";
import { setSessionStorage } from "../../sessionHelper";

function AdminManagement() {
  const [userFilter, setUserFilter] = useState("Overall");
  const {isPreview, setIsPreview} = usePreviewStore();
  const [data, setData] = useState([]);
  const [datas, setDatas] = useState([]);
  const {selectedData, setSelectedData} = useLOIData();
  let navigate = useNavigate();
  const [search, setSearch] = useState("");
  const { setMessage } = useUserPopupStore();

  const fetchAdmins = async () => {
    try {
      const adminList = await axios.get("/auth/admins");
      setData(adminList.data);
      setDatas(adminList.data);
    } catch (e) {
      console.log("Unable to fetch admins", e);
    }
  };

  useEffect(() => {
    let filtered = [...datas];
  
    if (search) {
      filtered = filtered?.filter((admin) =>
        admin.username?.toLowerCase()?.includes(search?.toLowerCase())
      );
    }
  
    if (userFilter === "Active") {  
      filtered = filtered.filter((admin) => admin.is_active === true);
    } else if (userFilter === "Inactive") {
      filtered = filtered.filter((admin) => admin.is_active === false);
    }

    setData(filtered);
  }, [search, userFilter]);

  useEffect(() => {
    fetchAdmins();
    setSelectedData("assignedCourse",null)
    setSelectedData("sessions",null)
    setSelectedData("moduleLists",null)
    setSelectedData("moduleHeader",null)
    setSelectedData("scenarioHeader",null)
    setSelectedData("courseHeader",null)
  }, []);

  function formatDate(dateString) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    return `${day}-${month}-${year}`;
  }

  const confirmPopup = (admin) => {
    return new Promise((resolve) => {
      setIsPreview({
        enable: true,
        msg: `Are you sure you want to delete the admin - ${admin.username} permanently?`,
        value: "ok/cancel",
        resolve,
      });
    });
  };
  
  const handleDelete = async (admin) => {
    const confirmed = await confirmPopup(admin);
    if (!confirmed) return;

    axios
      .delete(`/auth/admins/${admin.id}`)
      .then((res) => {
        setMessage({
          enable: true,
          msg: "Admin Deleted Successfully",
          state: true,
        });
        fetchAdmins()
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

  const handleAdmin = async(_) => {
    try {
      const adminList = await axios.get(`/auth/admins/${_}`);
      setSessionStorage("adminData", adminList)
      navigate(`/migoto-cms/admins/${_}/editAdmin`);
    } catch (e) {
      console.log("Unable to fetch admin", e);
    }
  }

  return (
    <>
      <div className={styles.mainBox}>
        <div className={styles.mainHeader}>
          <div className={styles.mainHeaderLeft}>
            <p>Admin List</p>
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
            <div className={styles.addUserBtn} onClick={()=>{navigate("createAdmin"),localStorage.setItem("currentPathLocation","Create Admin"),
              localStorage.setItem("TLData",JSON.stringify(TimeLineRoute["/migoto-cms/admins/createAdmin"]))}}>
              <div>
                <PlusIcon stroke={"white"} />
              </div>
              <div>Add Admin</div>
            </div>
            <div className={styles.searchBar}>
              <input type="text" placeholder="Search admin..." onChange={(e)=>{setSearch(e.target.value)}} />
              <div>
                <SearchIcon />
              </div>
            </div>
          </div>
        </div>

        <div className={styles.mainSection}>
          <div className={styles.sectionContent}>
            <table className={styles.userTable}>
              <thead className={styles.userThead}>
                <tr>
                  <th className={styles.userTh1}>S.no</th>
                  <th className={styles.userTh2}>Username</th>
                  <th className={styles.userTh3}>Employee Id</th>
                  <th className={styles.userTh4}>Email address</th>
                  <th className={styles.userTh6}>Created date</th>
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
                      <td>{formatDate(_.created_at)}</td>
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
                      <td>
                        <div className={styles.editColumn}>
                          <div
                            className={styles.editBox}
                            onClick={() => {
                              handleAdmin(_.id)
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

export default AdminManagement;