import React from 'react';
import { Link } from 'react-router-dom';
import { getTeamLogo } from '../utils/logos';

const NextGame = ({ game }) => {
  if (!game) return null;

  const [year, month, day] = game.date.split('-').map(Number);
  const gameDate = new Date(year, month - 1, day);
  const dateString = gameDate.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });
  const timeString = gameDate.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    timeZoneName: 'short',
  });

  return (
    <Link to={`/game/${game.id}`} state={{ game }} style={{ textDecoration: 'none', display: 'block' }}>
      <div className="next-game-hero">
        <h2>Next Game</h2>
        <div className="game-info">
        <div className="teams">
          <div className="team-container">
            <img src={getTeamLogo(game.opponent)} alt={game.opponent} className="team-logo large" />
            <span className="opponent">{game.opponent}</span>
          </div>
        </div>
        <div className="time-location">
          <p className="date">{dateString}</p>
          <p className="time">{game.time}</p>
          <p className="location">{game.isHome ? 'Chase Center' : ''}</p>
        </div>
        </div>
      </div>
    </Link>
  );
};

export default NextGame;
