import React from "react";
import styles from "../../Pages/HeroPage/HeroPage.module.css";

function HeaderContent() {
  let checkPath = localStorage.getItem("currentPathLocation");

  return (
    <>
      {checkPath == "Create User" && (
        <p className={styles.pageDescription}>
          Create and Manage Users Here: Easily add new users, assign Module
        </p>
      )}
      {checkPath == "Dashboard" && (
        <p className={styles.pageDescription}>
          Monitor user performance, evaluate training effectiveness, and
          generate comprehensive reports with ease
        </p>
      )}
      {checkPath == "Assign Course" && (
        <p className={styles.pageDescription}>
          Create and Manage Course Here: Easily add new Course, assign Available
          courses
        </p>
      )}
      {checkPath == "Create Course" && (
        <p className={styles.pageDescription}>
          Create and Manage Courses Here: Easily add new courses, assign
          modules, and organize content effortlessly.
        </p>
      )}
      {checkPath == "User" && (
        <p className={styles.pageDescription}>
          Create and Manage Users Here: Easily add new users, assign Module
        </p>
      )}
      {checkPath == "Course Management" && (
        <p className={styles.pageDescription}>
          Create and Manage Course Here: Easily add new Course, assign Available
          courses
        </p>
      )}
      {checkPath == "Create Avatar" && (
        <p className={styles.pageDescription}>
          Create and Manage Avatars Here: Easily add new Avatar, assign Available
          courses
        </p>
      )}
      {checkPath == "Admin Management" && (
        <p className={styles.pageDescription}>
          Create and Manage Admins Here: Easily add new users to Admins
        </p>
      )}
    </>
  );
}

export default HeaderContent;
