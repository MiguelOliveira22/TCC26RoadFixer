import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'


import Header from "./components/Header"
import Navbar from "./components/Navbar"
import Banner from "./components/Banner"

function App() {
  return (
    <>
      <Header/>
      <Navbar/>
      <Banner/>
    </>
  )
}

export default App