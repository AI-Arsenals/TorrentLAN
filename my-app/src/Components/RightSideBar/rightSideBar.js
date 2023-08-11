
import { useEffect, useState } from "react";
import "../RightSideBar/rightSideBarStyles.css";






const RightSideBar = ({ rightCollapseButtonHandler, folder }) => {
  
  let [availability,setAvailability] = useState(null)
  let properties={}
  const preprocessProperties = () =>{
    
    properties['Name']=folder[1]
    properties = {...properties,...folder[5]}
    
  }
  preprocessProperties()
  
  
  const fetchUniqueIdIsUp = async()=>{
      let response,data;
      response = await fetch(`http://127.0.0.1:8000/api/unique_id_is_up?unique_id=${folder[7]}`)
      data = await response.json()
      setAvailability(data)
  }

  useEffect(()=>{
    setAvailability(null)
  },[folder])
  
  
  const AvailabilityInfo = ()=>{
    

      return <div className="availability-info">
      <div className="is-available">
        {availability['is_available']? 'Available':'Not Available'}
      </div>
      <div className="speed">
        Speed: {availability['speed']}
      </div>
    </div>
    
  }
  
  const AvailabilityInfoContainer = ()=>{
    
  
      return <div className="availability">
            <button className="simpleButton" id="availabilityCheckButton" onClick={()=>fetchUniqueIdIsUp()}>Current Availability</button>
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
