import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import GameDetails from './pages/GameDetails';

function App() {
  return (
    <Router>
      <div className="app-container">
        <header className="app-header">
          <h1>Warriors Schedule</h1>
        </header>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/game/:id" element={<GameDetails />} />
        </Routes>
        <footer>
          <p>Go Warriors!</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
