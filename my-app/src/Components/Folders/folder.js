import React from "react";
import "./folderStylesheet.css";
import { useState } from "react";
import { useEffect } from "react";

import FolderItem from "./folder-item";

const FolderView = (props) => {
  const [dir, setDir] = useState("root");
  
  const [contentList, setContentList] = useState({ folders: [], files: [] });
  const [dir_text, setDirText] = useState("root");
  const [downloadList, setDownloadList] = useState([]);
  const [currFolder, setCurrFolder] = useState([
    -1,
    "none",
    0,
    null,
    null,
    { Path:"root" ,Size: 89 },
    null,
    null,
    null,
  ]);

  const getFolderList = async () => {
    let response, data,depth;
    if(currFolder[5].Path==null){
      depth=2;
    }
    else{

      depth=currFolder[5].Path.split('//').length
    }

    if (depth ===1) {
      response = await fetch(
        `api/getFolderListAtDepth?depth=${depth}&folder=none`
      );
    }
    else if(depth ===2){
      response = await fetch(
        `api/getFolderListAtDepth?depth=${depth}&folder=${currFolder[1]}`
      );
    }
    else{
      response = await fetch(
        `api/getFolderList?unique_id=${currFolder[7]}&lazy_file_hash=${currFolder[6]}`
      );
    }
    data = await response.json();
    setContentList(data);
    await setDir(currFolder[5].Path)
  };

  const deselectAll = () => {
    setDownloadList([]);

    var list = document.querySelectorAll(".selected");
    list.forEach((element) => {
      element.classList.remove("selected");
    });
  };

  const select = (name) => {
    console.log(downloadList.find((e) => e === name));
    if (downloadList.find((e) => e === name)) {
      setDownloadList((prev) => prev.filter((e) => e !== name));
    } else {
      setDownloadList((prev) => [...prev, name]);
    }
  };

  const downloadHandler = () => {
    console.log(downloadList);
  };

  useEffect(() => {
    getFolderList();
    
    deselectAll();
  }, [currFolder]);

  const backButtonHandler = () => {
    setDir((data) => {
      if (data !== "root") {
        const i = data.lastIndexOf("%");
        return data.slice(0, i);
      }
      return data;
    });
  };

  return (
    <div className="main-container">
      <div className="viewport">
        <div className="navbar">
          <div className="left-content">
            <i
              className="fa-solid fa-arrow-left fa-2xl"
              onClick={backButtonHandler}
            ></i>
            <div className="dir-text">{dir}</div>
          </div>

          <div className="right-content">
            {downloadList.length > 0 ? (
              <i
                className="fa-regular fa-circle-down fa-2xl"
                onClick={downloadHandler}
              ></i>
            ) : (
              <div></div>
            )}
          </div>
        </div>

        {contentList["folders"].map((item, index) => (
          <FolderItem
            key={index}
            name={item[1]}
            type="folder"
            handleClick={async ()=>{await setCurrFolder(item)}}
            handleRightClick={() => select(item[1])}
          />
        ))}

        {contentList["files"].map((item, index) => (
          <FolderItem
            key={index}
            name={item[1]}
            type="file"
            handleRightClick={() => select(item[1])}
            handleClick={() => 1}
          />
        ))}
      </div>
    </div>
  );
};

export default FolderView;
