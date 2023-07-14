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

    if(destFolder===null){
      alert("Please select destination folder")
      return;
    }

    let data;

    path.forEach(async p=>{

      data = { source_path: p, dest_path: destFolder["value"] };
    data = JSON.stringify(data);
    await fetch("api/upload", {
      method: "POST",
      data: data,
      body: data,
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    });

    })
    
    alert("Upload successful");
    console.log("upload successful", {});
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
        id="uploadButton"
        onClick={uploadButtonHandler}
        disabled={!uploadButtonVisible}
      >
        Upload
      </button>
    </div>
  );
};

export default Upload;
