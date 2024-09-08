
import List from '../component/List'
import { useNavigate } from 'react-router-dom';
import '../cart.css'
import { useState } from 'react';
import product from '../data/product.json'

function Cart(props){

    const prev = [...props.prod];

       var cat = product.filter((obj)=>{
        if(prev[obj.id])
          return true;
        return false;
      })
  
      const item = cat;
      const empty = Object.keys(cat).length === 0;
      


    const [placed ,setPlaced] = useState(0)
    const navigate = useNavigate()
    

    function handleClick(){
        navigate("/order/category")
    }

    function handleOrder(){
        
        const placeButton = document.getElementById("placed-order")
        setPlaced(1);
        if(!empty){
        placeButton.innerHTML='<div id="successful">Succesfully placed<span id="plus" onClick=window.location.href=\'/order/category\'> + </span></div>'
       }else{
        placeButton.innerHTML = `<div class="place-order" id="placed-order">
                Place Order
            </div>`

       }
}

    const sum = product.reduce((accumulator, currentValue) => {
        if(prev[currentValue.id]){

            return (currentValue.price * prev[currentValue.id]) + accumulator;
        }
        return accumulator;

    }, 0);
    const cost = sum;

    return(
        <div>
             <div class="cat-search">
             <div class="lessthan" onClick={handleClick}>&lt;</div>
             </div>
             {(!empty)?<div class="cost">Total Cost : {cost}</div>:<div></div>}
            { (placed === 0)?<List product={"all"} prod={props.prod} setProd={props.setProd}/> : <div></div>}

            <div class="place-order" id="placed-order" onClick={handleOrder}>
                Place Order
            </div>
        </div>
    )

}

export default Cart;