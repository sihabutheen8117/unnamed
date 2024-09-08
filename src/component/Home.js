import pizza from '../images/pizza.jpeg'
import '../home.css'
import { useNavigate } from 'react-router-dom';


function Home() {

    const navigate = useNavigate()

    function handleClick(){
        navigate("/order/place")
    }
    
    return(
        <>
            <img id="home_img" src={pizza} />
            <div id="enter_home">
                <div id="hungry">Are You Hungry ?</div>
                <div id="enter">
                    <div id="text" onClick={handleClick}>Lets taste !</div>
                </div>
            </div>
        </>
    )
}

export default Home;
