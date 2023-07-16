
import { useState } from "react";
import "../RightSideBar/rightSideBarStyles.css";






const RightSideBar = ({ rightCollapseButtonHandler, folder }) => {
  
  let [availability,setAvailability] = useState({
    'is_available':0,
    'speed': 'speed'
  })
  let properties={}
  const preprocessProperties = () =>{
    properties['Name']=folder[1]
    properties = {...properties,...folder[5]}
    
  }
  preprocessProperties()
  
  const fetchUniqueIdIsUp = async()=>{
      let response,data;
      response = await fetch(`api/unique_id_is_up?unique_id=${folder[7]}`)
      data = await response.json()
      console.log(data)
  }
  
  
  const AvailabilityInfo = ()=>{
    

      return <div className="availability-info">
      <div className="is-available">
        Available: {availability['is_available']}
      </div>
      <div className="speed">
        Speed: {availability['speed']}
      </div>
    </div>
    
  }
  
  const AvailabilityInfoContainer = ()=>{
    
  
      return <div className="availability">
            <button className="simpleButton" id="availabilityCheckButton" onClick={()=>fetchUniqueIdIsUp()}>Check Availability</button>
            {(availability!==null) && <AvailabilityInfo/>}
      </div>
    
  }
  
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
          })}
        </ul>

        
        {(folder[0]>0) && <AvailabilityInfoContainer/>}
      </div>
    </div>
  );
};

export default RightSideBar;
