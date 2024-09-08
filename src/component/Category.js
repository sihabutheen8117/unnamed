import { useLocation ,useNavigate} from "react-router-dom";
import '../category.css';
import pizza from '../images/pizza.jpeg'
import juice from '../images/orang juice.jpeg'
import burger from '../images/plain burger.jpeg';
import sandwich from '../images/cheesy sandwich.jpeg';
import Footer from './Footer'

function Category() {

    const location = useLocation()
    const navigate = useNavigate()

    function handleClick(){
        navigate("/order/place")
    }
    function handleItem(item){

        navigate("/order/add" ,{
            state : {
                category : item,
            }
        })
    }
    return(
        <>
            <div class="cat-search">
                <div class="lessthan" onClick={handleClick}>&lt;</div>
                <div class="cat-input"><input type="text" placeholder="search Dish"/> </div>
            </div>
            <div class="box">
                <div>You Make a click ,</div>
                <div>We make your food</div>
            </div>
            <div class="cat-header">Categories</div>
            <div class="categories">
                <div class="items" onClick={() => handleItem('burger')}><img src={burger}/>Burger</div>
                <div class="items" onClick={() => handleItem('pizza')}>pizza</div>
                <div class="items" onClick={() => handleItem('sandwich')}>Sandwich</div>
                <div class="items" onClick={() => handleItem('juice')}>juices</div>
                <div class="cat-more">More</div>
            </div>
            <Footer/>
        </>
    )
}

export default Category;
