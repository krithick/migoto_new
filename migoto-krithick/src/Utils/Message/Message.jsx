import React, { useEffect } from "react";
import styles from "./Message.module.css";
import { message } from "antd";
import { useUserPopupStore } from "../../store";

function Message() {
  const { message, setMessage } = useUserPopupStore();
  useEffect(() => {
    setTimeout(() => {
        setMessage({enable:false})
    }, 3000);
  }, [])


  return (
    <>
      <div className={styles.container}>
        <span className={styles.checkIcon}>
          <img src={message.state ? "/success.png" : "/error.png" } alt="" width={"35px"} />
        </span>
        <span className={styles.text}>{message.msg}</span>
      </div>
    </>
  );
}

export default Message;
