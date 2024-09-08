import '../place.css'
import { useNavigate } from 'react-router-dom';
import Footer from './Footer'

function Place() {

    const navigate = useNavigate()

    function handleClick(select){
        navigate("/order/category" ,{
            state : {
                place : select,
            }
        })
    }

    return(
        <>
            <div class='box'>
                <div >Eat ,Sip</div>
                <div >But don't Waste it</div>
                
            </div>
            <h1>Select Your table</h1>
            <div class="place">
                <div class='number' onClick={()=>{handleClick(1)}}>1</div>
                <div class='number' onClick={()=>{handleClick(2)}}>2</div>
                <div class='number' onClick={()=>{handleClick(3)}}>3</div>
                <div class='number' onClick={()=>{handleClick(4)}}>4</div>
                <div class='number' onClick={()=>{handleClick(5)}}>5</div>
                <div class='number' >▼</div>
            </div>
            <Footer/>

        </>
    )
}

export default Place;
