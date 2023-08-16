import React from "react";
import "../RightSideBar/rightSideBarStyles.css";

const RightSideBar = ({ rightCollapseButtonHandler, folder }) => {
  const properties = {
    Name: folder[1],
    ...folder[5]
  };

  return (
    <div className="rightSideBarWrapper">
      <div className="header">
        <div className="rightCollapseButtonContainer">
          <div
            className="rightCollapseButton"
            onClick={rightCollapseButtonHandler}
          >
            <i className="fa-solid fa-chevron-right fa-xl"></i>
          </div>
        </div>
        <div className="heading">
          <h4>Properties</h4>
        </div>
      </div>
      <div className="rightSideBarContent">
        <ul className="properties-list">
          {Object.keys(properties).map((property, index) => {
            if (property !== "availability") {
              return (
                <li className="property-item" key={index}>
                  <div className="property">{property}</div>
                  <div className="property-value">{properties[property]}</div>
                </li>
              );
            }
            return null; // Add this line to handle the case when property is "availability"
          })}
        </ul>
        <div className="message">
          <p>
            To download files, please download the software from{" "}
            <a href="https://github.com/AI-Arsenals/TorrentLAN">
              https://github.com/AI-Arsenals/TorrentLAN
            </a>
          </p>
          <p>
            Use the right-click of the mouse to get options for downloading
            inside the downloaded TorrentLAN software.
          </p>
        </div>
      </div>
    </div>
  );
};

export default RightSideBar;
