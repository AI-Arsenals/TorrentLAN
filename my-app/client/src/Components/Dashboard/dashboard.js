import React, { useEffect, useState } from "react";
import axios from "axios";
import CircularProgressBarWithLabel from '../CircularProgressBar/circularProgressBarWithLabel'
import CircularProgress from '@mui/material/CircularProgress';
import "../Dashboard/dashboardStyles.css";



const BytesInfo = () => {
  return (
    <div className="byte-info">
      <div className="children">Bytes downloaded</div>
      <div className="children">Bytes uploaded</div>
    </div>
  );
};

const FileCard = ({ file, index }) => {
  const file_loc=file["file_location"]
  const openFileLocation=()=>{
    axios.post('http://127.0.0.1:8000/api/openFileLocation',{'location':file_loc})
    
    
  }
  return (
    <div className="file-card" id={`temp${index}`}>
      <div className="sno">{index}</div>
      <div className="download-upload">download</div>
      <div className="name">{file["name"]}</div>
      <div className="table-name">{file["table_name"]}</div>
      <div className="percentage"><i className="fa-sharp fa-regular fa-circle-check"></i></div>
      <div className="size">{file["Size"]}</div>
      <div className="location">< i className="fa-solid fa-regular fa-folder-open" onClick={openFileLocation}></i></div>
    </div>
  );
};

const ActiveFileCard = ({ file, index }) => {
  const file_loc=file["file_location"]
  const openFileLocation=()=>{
    axios.post('http://127.0.0.1:8000/api/openFileLocation',{'location':file_loc})
  }
  return (
    <div className="file-card" id={`index`}>
      <div className="sno">{index}</div>
      <div className="download-upload">download</div>
      <div className="name">{file["name"]}</div>
      <div className="table-name">{file["table_name"]}</div>
      <div className="percentage">{file["percentage"]}<CircularProgressBarWithLabel variant="determinate" value={file["percentage"]}/></div>
      <div className="size">{file["Size"]}</div>
      <div className="location">< i className="fa-solid fa-regular fa-folder-open" onClick={openFileLocation}></i></div>
    </div>
  );
};



const Header = ({ header }) => {
  return (
    <div className="download-info-header">
      <div className="file-card" id={`header`}>
        <div className="sno">{header[0]}</div>
        <div className="download-upload">{header[1]}</div>
        <div className="name">{header[2]}</div>
        <div className="table-name">{header[5]}</div>
        <div className="percentage">{header[6]}</div>
        {/* <div className="percentage"></div> */}
        <div className="size">{header[7]}</div>
        <div className="location">{header[8]}</div>
      </div>
    </div>
  );
};

const FetchRenderActiveFiles = ({fetchEntries}) => {
  // console.log('rendering active files')
  const [activeFiles, setActiveFiles] = useState([]);
  
  const fetchActiveEntries = async () => {
    let response = await fetch("http://127.0.0.1:8000/api/currentDownloads");
    let data = await response.json();
    console.log(data["content"],activeFiles)
    if(data['render']){
      console.log('rerendering')
      fetchEntries()
    }
    setActiveFiles(data["content"]);
  };

  useEffect(() => {
    let interval = setInterval(async () => {
      await fetchActiveEntries();
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  return (
    <>
      {activeFiles.map((file, i) => {
        return <ActiveFileCard file={file} index={i} key={i} />;
      })}
    </>
  );
};

const DownloadFilesInfo = ({ files,fetchEntries }) => {
  const header = [
    "Sno",
    "Download",
    "test_name",
    "unique_id",
    "lazy_file_hash",
    "table_name",
    "percentage",
    "Size",
    "file-location",
  ];

  return (
    <div className="download-files-info">
      <Header header={header} />

      <div className="download-info-content">
        <FetchRenderActiveFiles fetchEntries={fetchEntries} />
       
        {files.map((file, i) => {
          return <FileCard file={file} index={i} key={i} />;
        })}
      </div>
    </div>
  );
};





const Dashboard = () => {
  const [entries, setEntries] = useState([]);
  

  const fetchEntries = async () => {
    let response = await fetch("http://127.0.0.1:8000/api/dashboard_entries");
    let data = await response.json();

    setEntries(data["content"]);
  };

  

  // fetchEntries()
  useEffect(() => {
    fetchEntries();
  }, []);

  return (
    <div className="dashboard-container">
     
      
      <DownloadFilesInfo files={entries} fetchEntries={fetchEntries}/>
    </div>
  );
};

export default Dashboard;
