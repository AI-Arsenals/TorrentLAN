import { Component } from "react";
import { Link } from "react-router-dom";
import "./navbarStyles.css"
import { menuItems } from './menuItems';

class Navbar extends Component {


    render() {
        return (
            <>
                <nav className="Navbar-items" id="Navbar-items">
                    <h3 className="Navbar-logo">
                        LOGO
                    </h3>



                    <ul className="Navbar-menu">

                        {menuItems.map((item, index) => {
                            return (
                                <li key={index}>


                                    <Link className={item.cName} to={item.url}>

                                        <i className={item.icon}></i>{item.title}
                                    </Link>





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
