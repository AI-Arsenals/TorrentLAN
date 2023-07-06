import React from 'react'

import FolderView from '../Components/Folders/folder'
import SideBar from '../Components/Sidebar/sidebar'
import Dashboard from '../Components/Dashboard/dashboard'
import Upload from '../Components/Upload/upload'
import '../Routes/homeStyle.css'
import { Route, Routes } from "react-router-dom";

const Home = (props) => {

  
  
  return (
    <div className='main'>
      <div className="sidebar">

      <SideBar />
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
