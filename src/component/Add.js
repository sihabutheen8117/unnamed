import { useNavigate ,useLocation} from "react-router-dom";
import '../add.css'
import List from '../component/List.jsx'
import Footer from './Footer'
import { useState } from "react";

function Add(props){

    const navigate = useNavigate()
    const location = useLocation()
    const [filter ,setFilter] =useState("all")
    const [search ,setSearch] = useState("")

    function handleClick(){
        navigate("/order/category")
    }

    function handleFilter(type){
        setFilter(type)
    }

    const handleChange = (event) => {
        setSearch(event.target.value);
    };


    return(
        <div class="block">
            <div class="cat-search">
                <div class="lessthan" onClick={handleClick}>&lt;</div>
                <div class="cat-input"><input type="text" placeholder="seach Dish" onChange={handleChange}/> </div>
            </div>
            <div class="filter">
                <div onClick={()=>handleFilter("all")}>All</div>
                <div onClick={()=>handleFilter("veg")}>Veg</div>
                <div onClick={()=>handleFilter("non-veg")}>Non-veg</div>
            </div>
            <List search={search} filter={filter} product={location.state.category} prod={props.prod} setProd={props.setProd}/>
            <Footer/>
        </div>
    )
}

export default Add;