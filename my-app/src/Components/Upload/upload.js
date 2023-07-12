import React, { useEffect, useState } from 'react'
import DragDrop from '../DragDrop/DragDrop'
import LoadingBar from '../LoadingBar/loadingBar'
import './uploadStyles.css'

import {toast,ToastContainer} from 'react-toastify'
const Upload = (props) => {
  
  const [path,setPath] = useState([])
  const [uploadButtonVisible,setUploadButtonVisible] = useState(false)

  const findIntersection=(str1,str2)=>{
    
    const minlength = Math.min(str1.length,str2.length)
    var sliceInd=0
    for (let index = 0; index < minlength; index++) {
      
      if(str1[index]!==str2[index]){
        return str1.slice(0,sliceInd+1);
        
      }

      if(str1[index]=='\\'){
        sliceInd=index
      }
      
    }
    return str1.slice(0,minlength)
  }

  const findRootDir = ()=>{
    var intersection = path[0].slice(0,path[0].lastIndexOf('\\')+1);
    console.log("intersectio: "+intersection)
    for (let index = 1; index < path.length; index++) {
      intersection=findIntersection(intersection,path[index]);
      
    }
    return intersection
  }

  const getChildren = (rootDirLength)=>{
    var children = new Set([])
    var child="";
    var ind=0;
    for (let index = 0; index < path.length; index++) {
      ind=path[index].indexOf("\\",rootDirLength)
      ind=(ind>-1)? ind:path[index].length
     child=path[index].slice(rootDirLength,ind)
     children.add(child)
      
    }
    return children
  }

  useEffect(()=>{
    if (path.length>0) {
      setUploadButtonVisible(true)
    }
    else{
      setUploadButtonVisible(false)
    }
  },[path])

  const notify = () => {
    toast("Default Notification !");

    toast.success("Success Notification !", {
      position: toast.POSITION.TOP_CENTER
    });

    toast.error("Error Notification !", {
      position: toast.POSITION.TOP_LEFT
    });

    toast.warn("Warning Notification !", {
      position: toast.POSITION.BOTTOM_LEFT
    });

    toast.info("Info Notification !", {
      position: toast.POSITION.BOTTOM_CENTER
    });

    toast("Custom Style Notification with css class!", {
      position: toast.POSITION.BOTTOM_RIGHT,
      className: 'foo-bar'
    });}

  const uploadButtonHandler = ()=>{
    console.log(path)
    var rootDir = findRootDir()
    var children = getChildren(rootDir.length)
    let data={'source_path':rootDir}
    data=JSON.stringify(data)
    fetch('api/upload',{method:'POST',
    data: data,
    body:data,
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
    
  })
    alert("Upload successful")
    console.log('upload successful',{})
    setPath([])
  }
  return (
    <div className='upload-container'>
      
      <DragDrop className='default' setter={setPath}/>
      <LoadingBar progress='70' title='Uploading'/>

      <button id='uploadButton' onClick={uploadButtonHandler} disabled={!uploadButtonVisible}>Upload</button>
      
      <button onClick={notify}>Notify</button>;
          
    </div>
  )
}

export default Upload
