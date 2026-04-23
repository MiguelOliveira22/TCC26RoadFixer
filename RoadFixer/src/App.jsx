import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from "./components/Navbar"
import Banner from "./components/Banner"
import Stats from "./components/Stats"
import Features from "./components/Features"
import RecentAccidents from "./components/RecentAccidents"
import Footer from "./components/Footer"
import MapaPage from "./Pages/MapaPage" 
import SaibaMaisPage from "./Pages/saibaMaisPage"
import './App.css'

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <Routes>
          {/* Rota da Página Inicial */}
          <Route path="/" element={
            <main>
              <Banner />
              <Stats />
              <Features />
              <RecentAccidents />
            </main>
          } />
          
          {/* Rota da Página do Mapa */}
          <Route path="/mapa" element={<MapaPage />} />

          {/* Rota da pagina Saiba Mais */}
          <Route path="/saibaMais" element={<SaibaMaisPage />}/>

        </Routes>
        <Footer />
      </div>
    </Router>
  )
}

export default App;