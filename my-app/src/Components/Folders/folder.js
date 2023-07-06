import React from "react";
import "./folderStylesheet.css";
import { useState } from "react";
import { useEffect } from "react";

import FolderItem from "./folder-item";

const FolderView = (props) => {
  const defualtFolder=[
    'default',
    "none",
    0,
    null,
    null,
    { Path:"root_folder" ,Size: 89 },
    null,
    null,
    null,
  ]
  const [dir, setDir] = useState("root");
  
  const [contentList, setContentList] = useState({ folders: [], files: [] });
  const [dir_text, setDirText] = useState("root");
  const [downloadList, setDownloadList] = useState([]);
  const [currFolder, setCurrFolder] = useState(defualtFolder);

  const getFolderList = async () => {
    let response, data,depth;
    if(currFolder[0]==='default'){
      depth=0;
    }
    else if(currFolder[0]<0){
      depth=(-1)*currFolder[0];
    }
    else{
      depth=3;
    }

    

    if (depth ===1||depth===0) {
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
    if(currFolder[5].Path!=null){

      await setDir(currFolder[5].Path)
      
    }
  };

  const deselectAll = () => {
    setDownloadList([]);

    var list = document.querySelectorAll(".selected");
    list.forEach((element) => {
      element.classList.remove("selected");
    });
  };

  const select = (name) => {
    
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

  const backButtonHandler = async() => {
    let response,data
    if(currFolder[3]==null){
      if(currFolder[0]=='default'){
        return;
      }
      else if(currFolder[0]===-1){
        setCurrFolder(defualtFolder)
        return;
      }
      else if(currFolder[0]===-2){
        response = await fetch(
          `api/getFolderListAtDepth?depth=0&folder=none`
        );
        data=await response.json()
        setCurrFolder(data['folders'][0])
      }
    }

    else if(currFolder[5].Path.split('\\').length==3){
      let start,end,folder
      start=currFolder[5].Path.indexOf('\\')
      end=currFolder[5].Path.lastIndexOf('\\')
      folder=currFolder[5].Path.slice(start+1,end)
      response = await fetch(
        `api/getFolderListAtDepth?depth=1&folder=none`
      );
      data=await response.json()
      folder=data['folders'].find((item)=>{return item[1]===folder})
      folder[5]=jsonParser(folder[5])
      setCurrFolder(folder)

    }
    else{
      response=await fetch(`api/db_search?id=${currFolder[3]}`)
      
      data=await response.json()
      data=data['content'][0]
      // console.log(data[5])
      data[5]=jsonParser(data[5])
      setCurrFolder(data)
    }
    

  };

  const jsonParser=(ojson)=>{
    ojson = ojson.replace(/'/g, '"');
    
    return JSON.parse(ojson)
  }

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
            handleClick={async ()=>{item[5]=jsonParser(item[5]);await setCurrFolder(item) }}
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
