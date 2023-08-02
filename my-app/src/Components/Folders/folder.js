import React from "react";
import "./folderStylesheet.css";
import { useState } from "react";
import { useEffect } from "react";
import RightSideBar from "../RightSideBar/rightSideBar";
import FolderItem from "./folder-item";
import Snackbar from "../SnackBars/Snackbars";
const FolderView = (props) => {
  const [rightIsClosed, setRightIsClosed] = useState(false);

  const closed_Style = {
    flex: "0",
  };

  const open_style = {
    flex: "40%",
  };
  const defualtFolder = [
    -3,
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

  const [contentList, setContentListPrimitive] = useState({
    folders: [],
    files: [],
  });

  const [downloadList, setDownloadList] = useState([]);
  const [currFolder, setCurrFolder] = useState(defualtFolder);
  const [propertiesFolder, setPropertiesFolder] = useState([]);
  const [highlightedFolder, setHighlightedFolder] = useState(null);
  const [notify, setNotify] = useState({
    open: false,
    message: "",
    severity: "success",
    handleClose: () => {
      setNotify((prev) => ({ ...prev, open: false }));
    },
  });

  const alert = (message,severity)=>{
    setNotify(prev=>({
      ...prev,
      open: true,
      message: message,
      severity: severity
    }))


  }

  const setContentList = (data) => {
    setContentListPrimitive(data);
  };

  const getFolderList = async () => {
    let response, data, depth;

    if (currFolder.length == 1) {
      response = await fetch(`api/search_query?name=${currFolder[0]}`);
      depth = -1;
    } else if (currFolder[0] === -3) {
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
    } else if (depth > 0) {
      response = await fetch(
        `api/getFolderList?unique_id=${currFolder[7]}&lazy_file_hash=${currFolder[6]}`
      );
    }
    data = await response.json();
    if (data["Status"] === 200) {
      setContentList(data);
    } else {
      console.log("Something went wrong");
    }
    // if (currFolder[5].Path != null) {
    //   await setDir(currFolder[5].Path);
    // }
  };

  const deselectAll = async () => {
    await setDownloadList([]);

    var list = document.querySelectorAll(".selected");
    list.forEach((element) => {
      element.classList.remove("selected");
    });
  };

  const deselectHighlighted = () => {
    var list = document.querySelectorAll(".highlighted");
    list.forEach((element) => {
      element.classList.remove("highlighted");
    });

    setHighlightedFolder(null);
  };

  const handleClick = async (item) => {
    if (highlightedFolder === item) {
      if (item[2] === 0) {
        await setCurrFolder(item);
      }
    } else {
      await deselectAll();
      await deselectHighlighted();
      await setHighlightedFolder(item);
    }
  };

  const select = (name) => {
    deselectHighlighted();
    if (downloadList.find((e) => e === name)) {
      setDownloadList((prev) => prev.filter((e) => e !== name));
    } else {
      setDownloadList((prev) => [...prev, name]);
    }
  };

  const downloadFiles = async(downloadList)=>{
    let success=true;
    let count=0;
    let data;
    downloadList.map(async(file) => {
      data = {
        id: file[0],
        name: file[1],
        is_file: file[2],
        paernt_id: file[3],
        child_id: file[4],
        lazy_file_hash: file[6],
        Size: file[5]["Size"],
        unique_id: file[7],
        table_name: "Normal_Content_Main_Folder",
        file_location: "temp",
      };
      data = JSON.stringify(data);
      let response = await fetch("api/download", {
        method: "POST",
        body: data,
        headers: {
          "Content-type": "application/json; charset=UTF-8",
        },
      });

      data = await response.json()
      if(data['status']===false){
        success=false;
        
      }
      else{
        count++;
      }
    });
    return success;

  }

  const downloadHandler = async() => {
    console.log(downloadList);
    alert("download started. see Dashboard for more details","info")
    let downloadFilesList = downloadList
    deselectAll()
    let success = await downloadFiles(downloadFilesList); 
  };

  const switchFolder = async () => {
    await getFolderList();
    deselectHighlighted();
    deselectAll();
  };

  useEffect(() => {
    switchFolder();
  }, [currFolder]);

  useEffect(() => {
    let tempFolder;
    if (downloadList.length === 0 && highlightedFolder === null) {
      tempFolder = currFolder;
    } else if (highlightedFolder !== null) {
      tempFolder = highlightedFolder;
    } else {
      tempFolder = downloadList[downloadList.length - 1];
    }

    setPropertiesFolder(tempFolder);
  }, [currFolder, downloadList, highlightedFolder]);

  const backButtonHandler = async () => {
    deselectHighlighted();
    let response, data;

    if (currFolder.length == 1) {
      setCurrFolder(defualtFolder);
      return;
    } else if (currFolder[3] === null) {
      if (currFolder[0] === "default") {
        return;
      } else if (currFolder[0] === -1) {
        setCurrFolder(defualtFolder);
        return;
      } else if (currFolder[0] === -2) {
        response = await fetch(`api/getFolderListAtDepth?depth=0&folder=none`);
        data = await response.json();
        data = data["folders"][0];

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

      setCurrFolder(folder);
    } else {
      response = await fetch(`api/db_search?id=${currFolder[3]}`);

      data = await response.json();
      data = data["content"][0];
      // console.log(data[5])

      setCurrFolder(data);
    }
  };

  const Navbar = () => {
    return (
      <>
        <div className="left-content">
          <i
            className="fa-solid fa-arrow-left fa-2xl"
            onClick={backButtonHandler}
          ></i>

          <div className="dir-text">{dir}</div>
        </div>

        <div className="right-content">
          {downloadList.length > 0 && (
            <div className="downloadButtonContainer">
              {(currFolder[0] > 0 ||
                currFolder[0] === -2 ||
                currFolder.length === 1) && (
                <i
                  className="fa-regular fa-circle-down fa-2xl"
                  onClick={downloadHandler}
                ></i>
              )}

              <i
                className="fa-regular fa-circle-xmark fa-2xl"
                onClick={deselectAll}
              ></i>
            </div>
          )}
        </div>
      </>
    );
  };

  const SearchBar = () => {
    const [searchText, setSearchText] = useState("");

    const updateSearchText = (e) => {
      e.preventDefault();
      setSearchText(e.target.value);
    };

    const submitHandler = (e) => {
      e.preventDefault();
      console.log(searchText);
      setCurrFolder([searchText]);
    };
    return (
      <div className="search-wrapper">
        <form className="search-form" onSubmit={submitHandler}>
          <input
            type="text"
            placeholder="search"
            id="search-box"
            value={searchText}
            onChange={updateSearchText}
            onSubmit={submitHandler}
          />
        </form>
      </div>
    );
  };

  return (
    <div className="main-container">
      <Snackbar prop={notify} />
      <div className="downloadView">
        <div className="viewport">
          <div className="viewport-header">
            <div className="navbar">
              <Navbar />
            </div>
            <div className="search-bar">
              <SearchBar />
            </div>
          </div>

          {contentList["folders"].map((item, index) => {
            return (
              <FolderItem
                key={index}
                name={item[1]}
                type="folder"
                handleClick={() => handleClick(item)}
                handleRightClick={() => select(item)}
              />
            );
          })}

          {contentList["files"].map((item, index) => {
            return (
              <FolderItem
                key={index}
                name={item[1]}
                type="file"
                handleRightClick={() => select(item)}
                handleClick={() => handleClick(item)}
              />
            );
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
          folder={propertiesFolder}
        />
      </div>
    </div>
  );
};

export default FolderView;
