import React from 'react'
import './dragDropStyles.css'

const DragDrop = ({setter}) => {



    const dragOver = (e) =>{
        e.stopPropagation();
        e.preventDefault()
    }

    const drop = (e) =>{
        e.stopPropagation();
        e.preventDefault();

        const files = e.dataTransfer.files;
        let path=[]
        for(const file of files){
            path.push(file.path)
        }
        setter(path)
    }
  return (
    

        <div className="dropzone" onDragOver={dragOver} onDrop={drop}>
            drop your files here
        </div>
      
    
  )
}

export default DragDrop
