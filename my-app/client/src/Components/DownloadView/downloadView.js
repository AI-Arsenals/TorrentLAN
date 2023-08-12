import React from 'react'
import FolderView from '../Folders/folder'
import RightSideBar from '../RightSideBar/rightSideBar'
import '../DownloadView/downloadViewStyles.css'
import {useState} from 'react'

const DownloadView = () => {

  const [rightIsClosed,setRightIsClosed] = useState(false)
  const closed_Style ={
    
    flex: '0',
    
  }

  const open_style={
    flex: '20%'
  }
  return (
    <div className='downloadViewWrapper'>
      <div className="downloadView">
        <FolderView/>
      </div>
      <div className="rightSideBar" style={rightIsClosed? closed_Style:open_style}>
        <RightSideBar rightCollapseButtonHandler={async()=> setRightIsClosed((prev)=>!prev)}/>
      </div>
    </div>
  )
}

export default DownloadView
