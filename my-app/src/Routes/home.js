import React, { useState } from 'react'

// import FolderView from '../Components/Folders/folder'
import SideBar from '../Components/Sidebar/sidebar'
import Dashboard from '../Components/Dashboard/dashboard'
import DownloadView from '../Components/DownloadView/downloadView'
import Upload from '../Components/Upload/upload'
import FolderView from '../Components/Folders/folder'
import '../Routes/homeStyle.css'
import { Route, Routes } from "react-router-dom";

const Home = (props) => {

  const [isClosed,setIsClosed] = useState(false)
  const closed_Style ={
    
    flex: '0',
    
  }

  const open_style={
    flex: '20%'
  }
  
  return (
    <div className='main'>
      <div className="sidebar" style={isClosed? closed_Style:open_style}>

      <SideBar collapseButtonHandler={async()=>{await setIsClosed((isClosed)=> !isClosed)}}/>
      </div>

      <div className="home-content">


      <Routes>
        <Route path='' Component={Dashboard}/>
        <Route path='/download' Component={FolderView}/>
        <Route path='/upload' Component={Upload}/>
      </Routes>
      </div>
      
    </div>
  )
}

export default Home
