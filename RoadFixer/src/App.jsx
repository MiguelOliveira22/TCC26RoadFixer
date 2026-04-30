import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import HomePage from './Pages/HomePage';
import MonitoramentoPage from "./Pages/MonitoramentoPage";
import SaibaMaisPage from "./Pages/saibaMaisPage"; // Atenção ao nome do arquivo!
import './App.css';
import { pathObject } from './Constants';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar /> 
        
        <Routes>
          <Route path={pathObject.path}             element={<HomePage />} />
          <Route path={pathObject.children[0].path} element={<MonitoramentoPage />} />
          <Route path={pathObject.children[1].path} element={<SaibaMaisPage />} />
        </Routes>

        <Footer />
      </div>
    </Router>
  );
}

export default App;