import "../RightSideBar/rightSideBarStyles.css";



const fetchUniqueIdIsUp = async(unique_id)=>{
    let response,data;
    response = await fetch(`api/unique_id_is_up?unique_id=${unique_id}`)
    data = await response.json()
    console.log(data)
}


const AvailabilityInfo = ({availability})=>{
  return <div className="availability-info">
    <div className="is-available">
      Available: {availability['is_available']}
    </div>
    <div className="speed">
      Speed: {availability['speed']}
    </div>
  </div>
}

const AvailabilityInfoContainer = ({availability,unique_id})=>{
  if(availability){

    return <div className="availability">
          <button className="simpleButton" id="availabilityCheckButton" onClick={()=>fetchUniqueIdIsUp(unique_id)}>Check Availability</button>
          <AvailabilityInfo availability={availability}/>
    </div>
  }
}

const RightSideBar = ({ rightCollapseButtonHandler, properties }) => {
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

        <AvailabilityInfoContainer availability={properties['availability']} unique_id={properties['unique_id']}/>
      </div>
    </div>
  );
};

export default RightSideBar;
