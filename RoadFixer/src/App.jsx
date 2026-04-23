import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import HomePage from './Pages/HomePage';
import MapaPage from "./Pages/MapaPage";
import SaibaMaisPage from "./Pages/saibaMaisPage"; // Atenção ao nome do arquivo!
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar /> 
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/mapa" element={<MapaPage />} />
          <Route path="/saibaMais" element={<SaibaMaisPage />} />
        </Routes>

        <Footer />
      </div>
    </Router>
  );
}

export default App;