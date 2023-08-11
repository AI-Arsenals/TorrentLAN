import React from "react";
import {NavLink} from 'react-router-dom'
import "../Sidebar/sidebarStyles.css";
import sidebarItems from "../Sidebar/sideBarItems";

const Sidebar = ({ collapseButtonHandler }) => {
  return (
    <div className="container" id="container">
      <ul className="sidebar-list">
        <li className="collapseButtonContainer">
          <div className="collapseButton" onClick={collapseButtonHandler}>
            <i
              className="fa-solid fa-chevron-left fa-xl"
              
            ></i>
          </div>
        </li>
        {sidebarItems.map((item, index) => (
          <li>
          {/* <li
            key={index}
            className="sidebar-items"
            id={window.location.pathname === item.url ? "active" : "inactive"}
            onClick={() => {
              window.location.pathname = item.url;
            }}
          >
            <div className="icon">
              <i className={item.icon}></i>
            </div>
            <div className="item-title">{item.title}</div>
          </li> */}

          <NavLink
          key={index}
          className="sidebar-items"
          activeClassName = "sidebar-items"
          to={item.url}
        >
          <div className="icon">
            <i className={item.icon}></i>
          </div>
          <div className="item-title">{item.title}</div>
        </NavLink>
        </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
