import React from 'react';
import { Link } from 'react-router-dom';
import { getTeamLogo } from '../utils/logos';

const ScheduleList = ({ games }) => {
  return (
    <div className="schedule-list glass-card">
      <h3>Upcoming Schedule</h3>
      <ul>
        {games.map((game) => {
          const gameDate = new Date(game.date);
          const dateString = gameDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            weekday: 'short',
          });
          const timeString = gameDate.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
          });

          return (
            <li key={game.id}>
              <Link to={`/game/${game.id}`} state={{ game }} className="schedule-item" style={{ textDecoration: 'none' }}>
                <div className="date-col">
                  <span className="day">{dateString}</span>
                  <span className="time">{game.time}</span>
                </div>
                <div className="opponent-col">
                  <img src={getTeamLogo(game.opponent)} alt={game.opponent} className="list-logo" />
                  <span className="opponent-name">
                    {game.isHome ? 'vs' : '@'} {game.opponent}
                  </span>
                </div>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default ScheduleList;
