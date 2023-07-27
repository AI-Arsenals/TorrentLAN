import React, { useState } from 'react'
import '../Dashboard/dashboardStyles.css'


const BytesInfo = () =>{

  return <div className="byte-info">
    <div className="children">
        Bytes downloaded
      </div>
      <div className="children">
        Bytes uploaded
      </div>
  </div>
}


const FileCard = ({file})=>{
  return <div className="file-card" id={`temp${file[0]}`}>
    <div className="sno">

      {file[0]}
    </div>
    <div className="download-upload">
      {file[1]}
    </div>
    <div className="name">
      {file[2]}
    </div>
    <div className="table-name">
      {file[5]}
    </div>
    <div className="percentage">
      {file[6]}
    </div>
    <div className="size">
      {file[7]}
    </div>
    <div className="location">
      {file[8]}
    </div>
  </div>
}

const Header = ({header})=>{
  return <div className="download-info-header">
    <FileCard file = {header}/>
  </div>
}



const DownloadFilesInfo = ({files}) =>{
  const header = ['Sno','Download','test_name','unique_id','lazy_file_hash','table_name','percentage','Size','file-location']

  
  
  return <div className="download-files-info">
    <Header header={header}/>
    <div className="download-info-content">

    {files.map(file=>{
      return <FileCard file = {file}/>
    })}
    </div>
    
  </div>
}

const Dashboard = () => {

  const [entries,setEntries] = useState([])

  const fetchEntries = async()=>{
    let response = await fetch('api/dashboard_entries')
    let data = await response.json()
    
    console.log(data)
  }

  fetchEntries()

  return (
    <div className='dashboard-container'>

      <BytesInfo/>
      <DownloadFilesInfo files={entries}/>
      
    </div>
  )
}

export default Dashboard
