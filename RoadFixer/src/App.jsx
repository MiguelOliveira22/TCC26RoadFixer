import Navbar from "./components/Navbar"
import Banner from "./components/Banner"
import Stats from "./components/Stats"
import Features from "./components/Features"
import RecentAccidents from "./components/RecentAccidents"
import Footer from "./components/Footer"
import './App.css'

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <main>
        <Banner />
        <Stats />
        <Features />
        <RecentAccidents />
      </main>
      <Footer />
    </div>
  )
}

export default App