import React, { useState } from 'react'
import styles from '../../Pages/HeroPage/HeroPage.module.css'
import HomeIcon from '../../Icons/HomeIcon'
import { NavBarMatchRoute } from '../../RouteHelper/NavBarMatchRoute.js';
import {NavBar} from '../../RouteHelper/NavBar.js'
function NavBarComponent() {

    const pathLocation1 = NavBarMatchRoute(window.location.pathname);
  const [currentUser, setCurrentUser] = useState(JSON.parse(localStorage.getItem("user")));

  return (
    <>
            <div className={styles.navBar}>
          <div>
            <div className={styles.homeIcon}>
              <HomeIcon />
            </div>
            <div className={styles.items}>
              {pathLocation1?.map((item, i) => (
                <div key={i}>
                  <span>{">"}</span>
                  {item}
                </div>
              ))}
            </div>
          </div>
          <div className={styles.userDetail}>
            <div className={styles.initial}>
              <p>{currentUser?.username?.charAt(0)?.toUpperCase()}</p>
            </div>
            <div className={styles.name}>
              <p>{currentUser?.username}</p>
              <div>{currentUser?.role}</div>
            </div>
          </div>
        </div>

    </>
  )
}

export default NavBarComponent