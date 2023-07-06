import React, { useEffect } from 'react'
import '../RightSideBar/rightSideBarStyles.css'
const RightSideBar = ({rightCollapseButtonHandler}) => {

    const properties ={
        prop1:"prop1",
        prop2:"prop2",
        prop3:"prop3",
        prop4:"prop4",
        prop5:"prop5",
        prop6:"prop6",


    }

    

   
  return (
    <div className='rightSideBarWrapper'>
      <div className="header">
        <div className="rightCollapseButtonContainer">
          <div className="rightCollapseButton" onClick={rightCollapseButtonHandler}>

        <i className="fa-solid fa-chevron-right fa-xl"></i>
          </div>
        </div>
        <div className="heading">
            Properties
        </div>
      </div>
      <div className="content">
        <ul className="properties-list">
          {Object.keys(properties).map((property,index)=>(
            <li className="property-item" key={index}>
              <div className="property">
                {property}
              </div>
              <div className="property-value">
                {properties[property]}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default RightSideBar
