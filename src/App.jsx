import { useEffect } from 'react';
import { BrowserRouter as Router, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import AppData from './lib/AppData';
import BottomNav from './components/BottomNav';
import Home from './pages/Home';
import Schedule from './pages/Schedule';
import GamePreview from './pages/GamePreview';
import News from './pages/News';
import Standings from './pages/Standings';

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

function App() {
  return (
    <Router>
      <AppData>
        <ScrollToTop />
        <div className="app">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/schedule" element={<Schedule />} />
            <Route path="/schedule/previous" element={<Schedule previous />} />
            <Route path="/game/:id" element={<GamePreview />} />
            <Route path="/standings" element={<Standings />} />
            <Route path="/news" element={<News />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <BottomNav />
        </div>
      </AppData>
    </Router>
  );
}

export default App;
