import React, { useEffect, useState } from "react";

import DefaultDragDrop from "../DefaultDragDrop/dragDrop";
import "./uploadStyles.css";
import Select from "react-select";

const Upload = (props) => {
  const [path, setPath] = useState([]);
  const [uploadButtonVisible, setUploadButtonVisible] = useState(false);






  useEffect(() => {
    if (path.length > 0) {
      setUploadButtonVisible(true);
    } else {
      setUploadButtonVisible(false);
    }
  }, [path]);



  const uploadButtonHandler = async () => {

    if (destFolder === null) {
      alert("Please select destination folder")
      return;
    }

    let data;
    if (navigator.userAgent.toLowerCase().includes("win")) {
      alert("Click on yes on the permission to upload");
      console.log("Click on yes on the permission to upload", {});
      setTimeout(function() {
        // 1.0 sec wait time so user can read the alert
      }, 1000);
      // Devloper- instead of timeout we can run below commands once it click on OK in the alert box
    }
    else{
      alert("Devloper (please remove this alert)(as os is not windows so no need to click on allow)");
      console.log("Devloper (please remove this alert)(as os is not windows so no need to click on allow)", {});
    }


    

      data = { source_path: path, dest_path: destFolder["value"] };
    data = JSON.stringify(data);
    await fetch("api/upload", {
      method: "POST",
      data: data,
      body: data,
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    });

    
  

    setPath([]);
  };

  const options = [
    { value: "Games", label: "Games" },
    { value: "Music", label: "Music" },
    { value: "Movies", label: "Movies" },
  ];
  const [destFolder, setDestFolder] = useState(null);
  const DropDown = () => {

    return (
      <>
        <Select
          options={options}
          defaultValue={destFolder}
          onChange={setDestFolder}
          theme={(theme) => ({
            ...theme,
            borderRadius: 0,
            colors: {
              ...theme.colors,
              primary25: "hotpink",
              primary: "white",
              secondary: "purple",
              neutral0: "black",
              neutral80: "#ffffff",
            },
          })}
        />
      </>
    );
  };
  return (
    <div className="upload-container">
      {/* <DragDrop className='default' setter={setPath} setFetchingPath={setFetchingPath}/> */}
      <DefaultDragDrop setter={setPath} />
      {/* <LoadingBar progress='70' title='Uploading'/> */}

      <div className="dropdown">
        <DropDown />
      </div>

      <button
        className="simpleButton"
        onClick={uploadButtonHandler}
        disabled={!uploadButtonVisible}
      >
        Upload
      </button>
    </div>
  );
};

export default Upload;
