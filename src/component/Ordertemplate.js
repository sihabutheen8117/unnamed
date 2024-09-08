import {Outlet} from'react-router-dom'
import '../ordertemplate.css'
function Ordertemplate() {
    return(
        <>
            <div class="top">
                <button class='top-button'>O</button>
                <div id='top-right'>salman faris  <button class='top-button'>!</button></div>
            </div>          
            <Outlet/>
        </>
    )
}

export default Ordertemplate;
