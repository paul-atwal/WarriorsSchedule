import React, { useState, useEffect } from 'react';
import NextGame from '../components/NextGame';
import LastGame from '../components/LastGame';
import ScheduleList from '../components/ScheduleList';

function Home() {
  const [lastGame, setLastGame] = useState(null);
  const [nextGame, setNextGame] = useState(null);
  const [upcomingGames, setUpcomingGames] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("Home: useEffect triggered");
    
    const fetchLastGame = async () => {
      try {
        const res = await fetch('/api/last-game');
        if (res.ok) {
          const data = await res.json();
          setLastGame(data);
        }
      } catch (error) {
        console.error("Error fetching last game:", error);
      }
    };

    const fetchSchedule = async () => {
      try {
        const res = await fetch('/api/schedule');
        if (res.ok) {
          const games = await res.json();
          if (games.length > 0) {
            setNextGame(games[0]);
            setUpcomingGames(games.slice(1));
          }
        }
      } catch (error) {
        console.error("Error fetching schedule:", error);
      }
    };

    const loadAll = async () => {
      setLoading(true);
      await Promise.all([fetchLastGame(), fetchSchedule()]);
      setLoading(false);
    };

    loadAll();
  }, []);

  if (loading) {
    return <div className="app-container" style={{textAlign: 'center', paddingTop: '50px'}}>Loading...</div>;
  }

  return (
    <main>
      {!lastGame && !nextGame && upcomingGames.length === 0 && (
        <div className="glass-card" style={{textAlign: 'center', padding: '40px', marginTop: '20px'}}>
          <h2>No Schedule Data Available</h2>
          <p>Unable to load game data. Please ensure the backend server is running.</p>
        </div>
      )}

      {lastGame && (
        <section className="info-grid">
          <LastGame game={lastGame} />
        </section>
      )}
      
      {nextGame && (
        <section className="hero-section">
          <NextGame game={nextGame} />
        </section>
      )}

      {upcomingGames.length > 0 && (
        <section className="list-section">
          <ScheduleList games={upcomingGames} />
        </section>
      )}
    </main>
  );
}

export default Home;
