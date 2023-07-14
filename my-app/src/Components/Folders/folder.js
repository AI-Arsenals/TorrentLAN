import React from "react";
import "./folderStylesheet.css";
import { useState } from "react";
import { useEffect } from "react";
import RightSideBar from "../RightSideBar/rightSideBar";
import FolderItem from "./folder-item";



const FolderView = (props) => {
  const [rightIsClosed, setRightIsClosed] = useState(false);
  
  const closed_Style = {
    flex: "0",
  };

  const open_style = {
    flex: "40%",
  };
  const defualtFolder = [
    "default",
    "none",
    0,
    null,
    null,
    { Path: "root_folder", Size: 89 },
    null,
    null,
    null,
  ];
  const [dir, setDir] = useState("root");

  const [contentList, setContentListPrimitive] = useState({ folders: [], files: [] });

  const [downloadList, setDownloadList] = useState([]);
  const [currFolder, setCurrFolder] = useState(defualtFolder);
  const [properties, setProperties] = useState([]);
  const [highlightedFolder,setHighlightedFolder] = useState(null);

  const setContentList = (data)=>{
    data['folders'].forEach((item,index,array)=>{
      array[index][5]=jsonParser(array[index][5])
    })
    data['files'].forEach((item,index,array)=>{
      array[index][5]=jsonParser(array[index][5])
    })
    setContentListPrimitive(data)
  }

  const getFolderList = async () => {
    let response, data, depth;
    if (currFolder[0] === "default") {
      depth = 0;
    } else if (currFolder[0] < 0) {
      depth = -1 * currFolder[0];
    } else {
      depth = 3;
    }

    if (depth === 1 || depth === 0) {
      response = await fetch(
        `api/getFolderListAtDepth?depth=${depth}&folder=none`
      );
    } else if (depth === 2) {
      response = await fetch(
        `api/getFolderListAtDepth?depth=${depth}&folder=${currFolder[1]}`
      );
    } else {
      response = await fetch(
        `api/getFolderList?unique_id=${currFolder[7]}&lazy_file_hash=${currFolder[6]}`
      );
    }
    data = await response.json();

    setContentList(data);
    if (currFolder[5].Path != null) {
      await setDir(currFolder[5].Path);
    }
  };

  const deselectAll = async() => {
    await setDownloadList([]);

    var list = document.querySelectorAll(".selected");
    list.forEach((element) => {
      element.classList.remove("selected");
    });
  };

  const deselectHighlighted = () =>{
    var list = document.querySelectorAll(".highlighted");
    list.forEach((element)=>{
      element.classList.remove("highlighted")
    })

    setHighlightedFolder(null)
  }

  const handleClick = async (item)=>{
    if(highlightedFolder===item){
      await setCurrFolder(item);
    }
    else{
      await deselectAll();
      await deselectHighlighted();
      await setHighlightedFolder(item)

    }
  }

  const select = (name) => {
    deselectHighlighted();
    if (downloadList.find((e) => e === name)) {
      setDownloadList((prev) => prev.filter((e) => e !== name));
    } else {
      setDownloadList((prev) => [...prev, name]);
    }
  };

  const downloadHandler = () => {
    console.log(downloadList);
  };


  const switchFolder = async() =>{
    await getFolderList();
    deselectHighlighted()
    deselectAll()
  }

  useEffect(() => {
    switchFolder()
  }, [currFolder]);

  useEffect(() => {
    let temp_properties={};
    if (downloadList.length === 0 && highlightedFolder===null) {
      temp_properties['Name']=currFolder[1];
      temp_properties={...temp_properties, ...currFolder[5]};
    } 
    
    else if(highlightedFolder!==null){
      temp_properties['Name']=highlightedFolder[1];
      temp_properties={...temp_properties,...highlightedFolder[5]};
    }
    else {
      temp_properties['Name']=downloadList[downloadList.length-1][1]
      temp_properties={...temp_properties,...downloadList[downloadList.length-1][5]};
      
    }
    setProperties(temp_properties)
  }, [currFolder, downloadList,highlightedFolder]);

  const backButtonHandler = async () => {
    
    deselectHighlighted();
    let response, data;
    if (currFolder[3] === null) {
      if (currFolder[0] === "default") {
        return;
      } else if (currFolder[0] === -1) {
        setCurrFolder(defualtFolder);
        return;
      } else if (currFolder[0] === -2) {
        response = await fetch(`api/getFolderListAtDepth?depth=0&folder=none`);
        data = await response.json();
        data = data["folders"][0];
        data[5] = jsonParser(data[5]);
        setCurrFolder(data);
      }
    } else if (currFolder[5].Path.split("\\").length === 3) {
      let start, end, folder;
      start = currFolder[5].Path.indexOf("\\");
      end = currFolder[5].Path.lastIndexOf("\\");
      folder = currFolder[5].Path.slice(start + 1, end);
      response = await fetch(`api/getFolderListAtDepth?depth=1&folder=none`);
      data = await response.json();
      folder = data["folders"].find((item) => {
        return item[1] === folder;
      });
      folder[5] = jsonParser(folder[5]);
      setCurrFolder(folder);
    } else {
      response = await fetch(`api/db_search?id=${currFolder[3]}`);

      data = await response.json();
      data = data["content"][0];
      // console.log(data[5])
      data[5] = jsonParser(data[5]);

      setCurrFolder(data);
    }
    console.log(currFolder);
  };

  const jsonParser = (ojson) => {
    ojson = ojson.replace(/'/g, '"');

    return JSON.parse(ojson);
  };

  return (
    <div className="main-container">
      <div className="downloadView">
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
                <div className="downloadButtonContainer">
                  <i
                    className="fa-regular fa-circle-down fa-2xl"
                    onClick={downloadHandler}
                  ></i>
                  
                  <i className="fa-regular fa-circle-xmark fa-2xl" onClick={deselectAll}></i>

                </div>
              ) : (
                <div></div>
              )}
            </div>
          </div>

          {contentList["folders"].map((item, index) => {
            
            return <FolderItem
              key={index}
              name={item[1]}
              type="folder"
              handleClick={() => handleClick(item)}
              handleRightClick={()=>select(item)}
            />;
          })}

          {contentList["files"].map((item, index) => {
            return <FolderItem
              key={index}
              name={item[1]}
              type="file"
              handleRightClick={() => select(item)}
              handleClick={() => 1}
            />
})}
        </div>
      </div>
      <div
        className="rightSideBar"
        style={rightIsClosed ? closed_Style : open_style}
      >
        <RightSideBar
          rightCollapseButtonHandler={async () =>
            setRightIsClosed((prev) => !prev)
          }
          properties={properties}
        />
      </div>
    </div>
  );
};

export default FolderView;
