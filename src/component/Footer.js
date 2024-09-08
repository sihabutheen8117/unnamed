import { useNavigate } from 'react-router-dom'
import '../footer.css'
import grocery from '../images/grocery-store.png'
import home from '../images/home.png'
import user from '../images/user.png'


function Footer(){
    const navigate = useNavigate();
    function handleOnClick(){
        navigate("/");
    }

    function handleGrocery(){
        navigate("/order/cart")
    }

    return(

        <div class='footer'>

            <div class="bar">
                <div class="img"><img src={home} onClick={handleOnClick}/></div>
                <div class="img"><img  src={user}/></div>
            </div>
            <div class="cart"><img src={grocery} onClick={handleGrocery}/></div>

        </div>

    )
}

export default Footer;