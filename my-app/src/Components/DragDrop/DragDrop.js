

import React, {useCallback} from 'react'
import {useDropzone} from 'react-dropzone'
import '../DragDrop/DragDropStyles.css'

const MyDropzone=({setter})=> {
  const onDrop = useCallback (async acceptedFiles => {
    // Do something with the files
    if(acceptedFiles?.length){
      let new_paths = acceptedFiles.map(file=>file.path)
      console.log(new_paths)
      await setter(new_paths)
    }
    
  }, [])
  const {getRootProps, getInputProps, isDragActive} = useDropzone({onDrop})

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
