import React from "react";
import FolderIcon from '../../assets/icons/folder-icon.png'
import FileIcon from '../../assets/icons/file-icon.png'

const FolderItem = (props) => {

  const makeActive=(event)=>{
    props.handleRightClick()
    if(event.target.classList.contains("selected")){
      event.target.classList.remove("selected")
    }
    else{
      event.target.classList.add("selected")
    }
  }

  

    
  return (
    <div className="folder-item" >
      <button className="folder-div" id={props.path} onClick={props.handleClick} onContextMenu={(event)=>{makeActive(event)}}>

        <img src={props.type==="folder"?FolderIcon:FileIcon} alt="folder-icon" className="folder-icon" />
      </button>
     
      <span className="folder-name">{props.name}</span> 
    </div>
  );
};

export default FolderItem;
