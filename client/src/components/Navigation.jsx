import React from "react";
import {Link} from "react-router-dom"; // use the link component from react-router-dom

function Navigation() {
    return (
        <nav>
            <ul>
                <li><Link to="/tutorials"> Not sure where to start? Watch a tutorial. </Link></li>
                <li><Link to="/faq"> Have a question? Check the FAQ page. </Link></li>
            </ul>
        </nav>
    );
}

export default Navigation;