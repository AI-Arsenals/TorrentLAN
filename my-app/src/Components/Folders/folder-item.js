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


  const handleLeftClick = async (event) =>{
    await props.handleClick()
    

    if(!event.target.classList.contains("highlighted")){
      event.target.classList.add("highlighted")
    }
  
      
    
  } 

  

    
  return (
    <div className="folder-item" >
      <button className="folder-div" id={props.path} onClick={(event)=> {handleLeftClick(event)}} onContextMenu={(event)=>{makeActive(event)}}>

        <img src={props.type==="folder"?FolderIcon:FileIcon} alt="folder-icon" className="folder-icon" />
      </button>
     
      <span className="folder-name">{props.name}</span> 
    </div>
  );
};

export default FolderItem;
