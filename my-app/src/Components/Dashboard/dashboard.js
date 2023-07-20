import React from 'react'
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



const DownloadFilesInfo = () =>{
  const header = ['Sno','Download','test_name','unique_id','lazy_file_hash','table_name','percentage','Size','file-location']
  const files = [
    
    [1,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [2,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [3,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [4,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [5,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [6,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [7,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [8,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [9,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [10,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [11,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],
    [12,'Download','Games','kfjsd;l','sdlfjsdfkljsdfkl','Normal content Main folder','100','49B','D:/torrantLan'],

  ]
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
  return (
    <div className='dashboard-container'>

      <BytesInfo/>
      <DownloadFilesInfo/>
      
    </div>
  )
}

export default Dashboard
