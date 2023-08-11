import {Route, Routes } from "react-router-dom";
import {HashRouter as HRouter} from 'react-router-dom'
import "./App.css";
import Navbar from "./Components/Navbar/navbar";
import Home from "./Routes/home";
import About from "./Routes/about";
import Temp from './Routes/temp'





function App() {

  

  return (
    <>
      <HRouter>
      
      <div className="wrapper">

          
          <Navbar />
          
          <div className="content">

            <Routes>
              <Route path="about" exact Component={About}/>
              <Route path="temp" exact Component={Temp}/>
              <Route path="/*" element={<Home/>} />
            </Routes>
          </div>
      </div>
      </HRouter>
    </>
  );
}

export default App;
