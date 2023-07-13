

import React, {useCallback} from 'react'
import {useDropzone} from 'react-dropzone'
import '../DragDrop/DragDropStyles.css'

const MyDropzone=({setter,setFetchingPath})=> {
  const onDrop = useCallback (async acceptedFiles => {
    // Do something with the files
    console.log("hello")
    
    if(acceptedFiles?.length){
      let new_paths = acceptedFiles.map(file=>file.path)
      console.log(new_paths)
      await setter(new_paths)
    }
    await setFetchingPath(false)
    
  }, [])

  const onDragEnter =useCallback(async =>{
    setFetchingPath(true)
  })

  const onDragLeave =useCallback(async =>{
    setFetchingPath(false)
  })

  const {getRootProps, getInputProps, isDragActive} = useDropzone({onDrop,onDragEnter,onDragLeave})

  return (
    <div {...getRootProps({className: 'dropzone'})}>
      <input {...getInputProps()} webkitdirectory="true"/>
      {
        isDragActive ?
          <p>Drop the files here ...</p> :
          <p>Drag 'n' drop some files here, or click to select files</p>
      }
    </div>
  )
}

export default MyDropzone
