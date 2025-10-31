import React, { useState } from "react";
import Background from "../Background/Background";
import styles from "./Login.module.css";
import UserIcon from "../../Icons/UserIcon.jsx";
import LockIcon from "../../Icons/LockIcon.jsx";
import Password from "antd/es/input/Password";
import { useNavigate } from "react-router-dom";
import { Input } from "antd";
import { useUserPopupStore } from "../../store";
import Message from "../../Utils/Message/Message";
import axios from '../../service.js'

function Login() {
  const navigate = useNavigate();
  const { message, setMessage } = useUserPopupStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
const [loading, setLoading] = useState(false)
  const fetchUser = () =>{
    axios
      .get("/auth/users/me")
      .then((res) => {
        localStorage.setItem("user",JSON.stringify(res.data));
        localStorage.setItem("role",res.data.role);
        navigate("dashboard");
        localStorage.setItem("currentPathLocation", "Dashboard");
        setLoading(false)
      })
      .catch((err) => {
        setMessage({
          enable: true,
          msg: "Something went wrong",
          state: false,
        });
        setLoading(false)
      });
  }

  let isValid = email?.trim() != "" && password?.trim() != "";

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      email: email?.trim(),
      password: password?.trim(),
    };
    setLoading(true)
    axios
      .post("/auth/login", data)
      .then((res) => {
        localStorage.clear()
        if(res?.data?.user_role=="user"){
          setMessage({
            enable: true,
            msg: "User Can't Login",
            state: false,
          });  
          setLoading(false)
          return
        }
        localStorage.setItem("migoto-cms-token", "Bearer "+res.data.access_token);
        fetchUser();
      })
      .catch((error) => {
        setMessage({
          enable: true,
          msg: error?.response?.data?.detail || "Something went wrong",
          state: false,
        });
        setLoading(false);
      });
  };

  return (
    <>
      <Background />
      {message.enable &&  <Message />}
      <div className={styles.mainContainer}>
        <img className={styles.illustration} src="/illustration3d.png" alt="" />
        <div className={styles.loginContainer}>
          <div className={styles.header}>
            <img className={styles.brand} src="/Logo.png" alt="" />
            <span className={styles.description}>
              Enhance your skills in a dynamic, interactive environment tailored
              to your learning needs.
            </span>{" "}
          </div>
          <form className={styles.loginForm} onSubmit={handleSubmit}>
            <span className={styles.heading}>Login</span>
            {/* Inputs */}
            <div className={styles.inputContainer}>
              <label className={styles.label}>
                <UserIcon /> Email
              </label>
              <input
                type="email"
                placeholder="Enter your Email"
                className={styles.input}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className={styles.inputContainer}>
              <label className={styles.label}>
                <LockIcon /> Password
              </label>
              <Input.Password
                type="password"
                placeholder="Enter your password"
                className={styles.input}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              className={styles.button}
              disabled={loading}
            >
              {!loading&&<p>Submit</p>}
              {loading&&<p className={styles.circle}></p>}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}

export default Login;