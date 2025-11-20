import React from 'react';
import { getTeamLogo } from '../utils/logos';

const LastGame = ({ game }) => {
  if (!game) return null;

  const gameDate = new Date(game.date);
  const dateString = gameDate.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });

  return (
    <div className="last-game-card glass-card">
      <h3>Last Game</h3>
      <div className="last-game-content">
        <div className="matchup-row">
          <img src={getTeamLogo(game.opponent)} alt={game.opponent} className="mini-logo" />
          <p className="matchup">
            vs {game.opponent} <span className="date">({dateString})</span>
          </p>
        </div>
        {game.youtubeLink && (
          <a
            href={game.youtubeLink}
            target="_blank"
            rel="noopener noreferrer"
            className="highlight-btn"
          >
            Watch Highlights
          </a>
        )}
      </div>
    </div>
  );
};

export default LastGame;
