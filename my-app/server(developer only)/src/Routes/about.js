import React from 'react';
import './about.module.css';
import axios from 'axios';
import hero_img from '../assets/hero_images/hero_1.jpg';
import HeroSection from '../Components/Hero_section/hero';

const About = () => {
  const linkStyle = {
    color: '#d9ff00',
    cursor: 'pointer', // Add a pointer cursor to make it clear it's clickable
    textDecoration: 'underline', // Add underline on hover
  };

  return (
    <div className='about_page'>
      <header>
        <h1>TorrentLAN</h1>
      </header>
      <section>
        <h2>How to Download</h2>
        <ul>
          <li>
            To download, use the right click of the mouse to select single or multiple files, then click on the download button to start the download.
          </li>
        </ul>
      </section>
      <section>
        <h2>How to Upload</h2>
        <ul>
          <li>Drag and drop files or folders to upload.</li>
          <li>Choose the place where you want to upload.</li>
          <li>Click on upload. If any popup is opened, click yes.</li>
        </ul>
      </section>
      <section>
        <h2>If you like this project, please give a star to this project at <a href='https://github.com/AI-Arsenals/TorrentLAN' style={linkStyle}>STAR</a></h2>
        <h2>To report any bug or feature request, create an issue at <a href='https://github.com/AI-Arsenals/TorrentLAN/issues' style={linkStyle}>ISSUES</a></h2>
      </section>
    </div>
  );
}

export default About;
