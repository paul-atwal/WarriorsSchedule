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
    const fetchData = async () => {
      try {
        console.log("Home: Fetching data...");
        setLoading(true);
        
        // Fetch Last Game
        const lastGameRes = await fetch('/api/last-game');
        console.log("Home: Last game status", lastGameRes.status);
        if (lastGameRes.ok) {
          const lastGameData = await lastGameRes.json();
          setLastGame(lastGameData);
        }

        // Fetch Schedule
        const scheduleRes = await fetch('/api/schedule');
        console.log("Home: Schedule status", scheduleRes.status);
        if (scheduleRes.ok) {
          const games = await scheduleRes.json();
          console.log("Home: Schedule data", games);
          if (games.length > 0) {
            setNextGame(games[0]);
            setUpcomingGames(games.slice(1));
          }
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
        console.log("Home: Loading set to false");
      }
    };

    fetchData();
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
