
import '../RightSideBar/rightSideBarStyles.css'
const RightSideBar = ({rightCollapseButtonHandler,properties}) => {

    

    

   
  return (
    <div className='rightSideBarWrapper'>
      <div className="header">
        <div className="rightCollapseButtonContainer">
          <div className="rightCollapseButton" onClick={rightCollapseButtonHandler}>

        <i className="fa-solid fa-chevron-right fa-xl"></i>
          </div>
        </div>
        <div className="heading">
            <h4>
            Properties
            </h4>
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
