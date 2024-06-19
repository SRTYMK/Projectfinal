import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Login from './components/Login';
import Signup from './components/Signup';
import './App.css';

function App() {
  const [showPopup, setShowPopup] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);

  const openAuthPopup = () => {
    setShowPopup(true);
    setIsRegistering(false);
  };

  const closePopup = () => {
    setShowPopup(false);
  };

  const toggleForm = () => {
    setIsRegistering(!isRegistering);
  };

  return (
    <Router>
      <div className="App">
        <Navbar openAuthPopup={openAuthPopup} />
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
        {showPopup && (
          <div className="popup-overlay">
            <div className="popup-content">
              <button className="close-popup" onClick={closePopup}>×</button>
              {isRegistering ? <Signup toggleForm={toggleForm} /> : <Login toggleForm={toggleForm} />}
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;
