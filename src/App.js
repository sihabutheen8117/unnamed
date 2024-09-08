import './App.css';
import {Routes ,Route } from 'react-router-dom'
import Home from './component/Home'
import Place from './component/Place'
import Ordertemplate from './component/Ordertemplate'
import Category from './component/Category'
import Add from './component/Add'
import { useState } from 'react';
import Cart from './component/Cart'

function App() {

  const [prod ,setProd] = useState([]);

  return (
    <div >
      <Routes>
        <Route path='/' element={<Home/>}/>
        <Route path='/order' element={<Ordertemplate/>}>
          <Route path='place'  element={<Place/>}/>
          <Route path='category' element={<Category/>}/>
          <Route path='add' element={<Add prod={prod} setProd={setProd}/>}/>
          <Route path='cart' element={<Cart prod={prod} setProd={setProd}/>} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;
