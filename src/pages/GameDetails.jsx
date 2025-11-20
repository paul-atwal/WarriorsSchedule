import React, { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { getTeamLogo } from '../utils/logos';

const GameDetails = () => {
  const { id } = useParams();
  const location = useLocation();
  const initialGame = location.state?.game;
  
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGameDetails = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/api/game/${id}`);
        if (!res.ok) {
          throw new Error('Game not found');
        }
        const data = await res.json();
        setGame(data);
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchGameDetails();
  }, [id]);

  // Fallback to initial state if API fails or is loading
  const displayGame = game || (initialGame ? {
    opponent: initialGame.opponent,
    record: "N/A",
    scorers: [],
    h2h: []
  } : null);

  if (loading && !displayGame) return <div className="glass-card" style={{padding: '20px', textAlign: 'center'}}>Loading game details...</div>;
  
  if (!displayGame) return <div className="glass-card" style={{padding: '20px', textAlign: 'center'}}>Game not found</div>;

  return (
    <div className="game-details-page">
      <Link to="/" className="back-link">← Back to Schedule</Link>
      
      <div className="glass-card header-card">
        <div className="matchup-header">
          <div className="team">
            <img src={getTeamLogo('Golden State Warriors')} alt="Warriors" className="header-logo" />
            <span>Warriors</span>
          </div>
          <div className="vs-badge">VS</div>
          <div className="team">
            <img src={getTeamLogo(displayGame.opponent)} alt={displayGame.opponent} className="header-logo" />
            <span>{displayGame.opponent}</span>
          </div>
        </div>
        <div className="game-meta">
          <p className="record">Opponent Record: {displayGame.record}</p>
        </div>
      </div>

      <div className="glass-card stats-card">
        <h3>Top Scorers (Season)</h3>
        {displayGame.scorers.length > 0 ? (
          <div className="scorers-grid">
            {displayGame.scorers.map((player, index) => (
              <div key={index} className="player-card">
                <img src={player.img} alt={player.name} className="player-img" />
                <div className="player-info">
                  <p className="name">{player.name}</p>
                  <p className="ppg">{player.ppg} PPG</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{textAlign: 'center', padding: '20px'}}>Stats not available yet.</p>
        )}
      </div>

      {displayGame.h2h.length > 0 && (
        <div className="glass-card h2h-card">
          <h3>Season Matchups</h3>
          <ul className="h2h-list">
            {displayGame.h2h.map((match, index) => (
              <li key={index} className="h2h-item">
                <span className="date">{match.date}</span>
                <span className="score">{match.score}</span>
                <span className={`result ${match.result === 'W' ? 'win' : 'loss'}`}>
                  {match.result}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default GameDetails;
