import React from 'react'
import './heroStyle.css'

const Hero = (props) => {
  return (
    <div className='hero-section'>
      <img src={props.img} alt="" />
    </div>
  )
}

export default Hero
