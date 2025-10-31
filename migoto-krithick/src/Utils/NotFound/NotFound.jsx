import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./NotFound.module.css";

function NotFound() {
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.title}>404</h1>
        <h2 className={styles.subtitle}>Page Not Found</h2>
        <p className={styles.message}>
          The page you are looking for doesn't exist or has been moved.
        </p>
        <button 
          className={styles.button}
          onClick={() => navigate("/migoto-cms/dashboard")}
        >
          Go to Dashboard
        </button>
      </div>
    </div>
  );
}

export default NotFound;