import React from "react";
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
          <li
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
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
