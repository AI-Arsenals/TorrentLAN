import React from "react";
import './loadingBarStyles.css'

const LoadingBar = ({progress,title}) => {

    const loaderChild={
        height: "100%",
        backgroundColor: "White",
        width: `${progress}%`,
        borderRadius: "10px"
    }

    

    
  return<>
  <div className="loadingBarWrapper">

   <div className="loaderParent">
        <div  style={loaderChild}>

        </div>
    </div>
    <div className="progressInfo">
        {title} ... {progress}%
    </div>
  </div>
    </>;
};

export default LoadingBar;
