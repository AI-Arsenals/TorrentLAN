import React, { useEffect, useState } from "react";
import DragDrop from "../DragDrop/DragDrop";
import LoadingBar from "../LoadingBar/loadingBar";
import DefaultDragDrop from "../DefaultDragDrop/dragDrop";
import "./uploadStyles.css";
import Select from "react-select";

const Upload = (props) => {
  const [path, setPath] = useState([]);
  const [uploadButtonVisible, setUploadButtonVisible] = useState(false);
  const [fetchingPath, setFetchingPath] = useState(false);

  const findIntersection = (str1, str2) => {
    const minlength = Math.min(str1.length, str2.length);
    var sliceInd = 0;
    for (let index = 0; index < minlength; index++) {
      if (str1[index] !== str2[index]) {
        return str1.slice(0, sliceInd + 1);
      }

      if (str1[index] == "\\") {
        sliceInd = index;
      }
    }
    return str1.slice(0, minlength);
  };

  const findRootDir = () => {
    var intersection = path[0].slice(0, path[0].lastIndexOf("\\") + 1);
    console.log("intersectio: " + intersection);
    for (let index = 1; index < path.length; index++) {
      intersection = findIntersection(intersection, path[index]);
    }
    return intersection;
  };

  const getChildren = (rootDirLength) => {
    var children = new Set([]);
    var child = "";
    var ind = 0;
    for (let index = 0; index < path.length; index++) {
      ind = path[index].indexOf("\\", rootDirLength);
      ind = ind > -1 ? ind : path[index].length;
      child = path[index].slice(rootDirLength, ind);
      children.add(child);
    }
    return children;
  };

  useEffect(() => {
    if (path.length > 0) {
      setUploadButtonVisible(true);
    } else {
      setUploadButtonVisible(false);
    }
  }, [path]);

  // const uploadButtonHandler = ()=>{
  //   console.log(path)
  //   var rootDir = findRootDir()
  //   var children = getChildren(rootDir.length)
  //   let data={'source_path':rootDir}
  //   data=JSON.stringify(data)
  //   fetch('api/upload',{method:'POST',
  //   data: data,
  //   body:data,
  //   headers: {
  //     "Content-type": "application/json; charset=UTF-8"
  //   }

  // })
  //   alert("Upload successful")
  //   console.log('upload successful',{})
  //   setPath([])
  // }

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
    const selectionChangeHandler = (event) => {
      setDestFolder(event.target.value);
    };
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
        {fetchingPath ? "Loading..." : "Upload"}
      </button>
    </div>
  );
};

export default Upload;
