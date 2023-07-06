import React, { useEffect, useState } from 'react'
import DragDrop from '../DragDrop/DragDrop'
import LoadingBar from '../LoadingBar/loadingBar'
import './uploadStyles.css'
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

  

  const uploadButtonHandler = ()=>{
    console.log(path)
    var rootDir = findRootDir()
    var children = getChildren(rootDir.length)
    console.log(rootDir)
    console.log(children)
    setPath([])
  }
  return (
    <div className='upload-container'>
      <DragDrop className='default' setter={setPath}/>
      <LoadingBar progress='70' title='Uploading'/>

      <button id='uploadButton' onClick={uploadButtonHandler} disabled={!uploadButtonVisible}>Upload</button>
    </div>
  )
}

export default Upload
