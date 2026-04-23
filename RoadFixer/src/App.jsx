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
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/mapa" element={<MapaPage />} />

          {/* Rota da pagina Saiba Mais */}
          <Route path="/saibaMais" element={<SaibaMaisPage />}/>

        </Routes>
      </div>
    </Router>
  );
}

export default App;
