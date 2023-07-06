import React from "react";
import "./folderStylesheet.css";
import { useState } from "react";
import { useEffect } from "react";

import FolderItem from "./folder-item";

const FolderView = (props) => {
  const [dir, setDir] = useState("root");
  const [contentList, setContentList] = useState({ folders: [], files: [] });
  const [dir_text, setDirText] = useState("root");
  const [downloadList,setDownloadList] = useState([])
  

  const getFolderList = async () => {
    let response = await fetch(`api/getEntries/${dir}`);
    let data = await response.json();
    setContentList(data);
    // console.log(data)
  };

  

  const deselectAll = ()=>{
    setDownloadList([])
    
    var  list = document.querySelectorAll(".selected")
    list.forEach(element=>{
      element.classList.remove("selected")
    })
  }

  const select=(name)=>{
    
    console.log(downloadList.find(e => e===name))
    if(downloadList.find(e=> e===name)){

      setDownloadList(prev=> prev.filter(e=> e!==name))
    }
    else{

      setDownloadList(prev=>[...prev,name])
    }
    
  }



  const downloadHandler = () =>{
    console.log(downloadList)
  }

 

  useEffect(() => {
    getFolderList();
    setDirText(() => {
      return dir.replaceAll("%", "/");
    });
    deselectAll()
    
  }, [dir]);

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
            <div className="dir-text">{dir_text}</div>
          </div>

          <div className="right-content">
            {downloadList.length>0?
          <i className="fa-regular fa-circle-down fa-2xl" onClick={downloadHandler}></i>: <div></div>}
          </div>
        </div>

        
          {contentList["folders"].map((name, index) => (
            <FolderItem
              key={index}
              name={name}
              type="folder"
              handleClick={() => setDir((dir) => (dir += "%" + name))}
              handleRightClick={()=> select(name)}
              
            />
          ))}

          {contentList["files"].map((name, index) => (
            <FolderItem
              key={index}
              name={name}
              type="file"
              
              handleRightClick={()=>select(name)}            
              handleClick={() => 1}
            />
          ))}
        
      </div>
    </div>
  );
};

export default FolderView;
