import '../list.css'
import product from '../data/product.json'
import { useState } from 'react';
import grocery from '../images/grocery-store.png'

function List(props){

    const search = props.search;
    const filter = props.filter;
    const select = props.prod;
    const setSelect = props.setProd;
    const prev = [...select];

    var cat ;

    const category = props.product;
    if(category !== "all"){
    cat = product.filter((obj)=>{
        if (obj.name.toLowerCase().includes(search.toLowerCase())){
        if(filter === "all")
          return obj.item === category;
        else{
          if(obj.type === filter)
            return obj.item === category;
        }
      }
    });
  }else{
    //cat = product ;
    cat = product.filter((obj)=>{
      if(prev[obj.id])
        return true;
      return false;
    })
    
  }

    const item = cat;


    function handleClick(id){
        setSelect((prev)=>{
          const newElem = [...prev]
          newElem[id]=(newElem[id] || 0) + 1;
          return newElem;

        })
    }
    function handleIncDec(id ,option){
      setSelect((prev)=>{
        const newElem = [...prev]
        newElem[id]=(newElem[id] || 0) + option;
        return newElem;

      })
    }

    
    var sum = 0;
    for(var i=0 ; i<40 ;i++)
    {
      sum = sum + ( prev[i] || 0 )
    }

    function add(id){
      if(select[id]){
        return <div class="add">
          <div onClick={()=>handleIncDec(id ,-1)}>-</div>
          <div>{select[id]}</div>
          <div onClick={()=>handleIncDec(id ,1)}>+</div>
          </div>
      }
      return <div class="add" onClick={()=>handleClick(id)}>ADD</div>
    }

    function handleGrocery(){
      return(
        <div>

        </div>
      )
    }

    return(
        <div class="menu">
      {(Object.keys(cat).length === 0)?<div  class="noitem">No items!</div>:item.map((productItem, id) => (
        <div key={id} >
          <div class="prod">
            <div class="left">
                <div class="menu-img"><img src={productItem.img}/></div>
                {add(productItem.id)}
            </div>
            <div class='right'>
                <div class="type">{productItem.type}</div>
                <div class="name">{productItem.name}</div>
                <div class="price">₹{productItem.price}</div>
                <div class="desc">{productItem.desc}</div>

            </div>
          </div>
        </div>
         )
        )
      }
    </div>
    
    )

}

export default List;