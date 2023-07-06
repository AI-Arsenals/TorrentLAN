import { Component } from "react";
import "./navbarStyles.css"
import {menuItems}  from './menuItems';

class Navbar extends Component{

    
    render(){
        return(
            <>
            <nav className="Navbar-items" id="Navbar-items">
                <h3 className="Navbar-logo">
                    LOGO
                </h3>


                
                <ul className="Navbar-menu">

                    {menuItems.map((item,index)=>{
                        return(
                            <li key={index}>
                        
                        <a className={item.cName} href={item.url}>

                        <i className={item.icon}></i>{item.title}
                        </a>
                       
                        
                        
                    </li>
                        )
                    })}

                    
                </ul>
            </nav>
            <div className="hidden"></div>
            </>
        )
    }
}

export default Navbar