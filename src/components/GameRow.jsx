import { Link } from 'react-router-dom';
import { dayOfMonth, dow, tipDate } from '../lib/time';
import { matchup } from '../lib/games';
import { TimeAndTv } from './Tv';
import { ChevronRight } from './Icons';

export function DateStack({ game }) {
  const d = tipDate(game);
  return (
    <div className="date-stack">
      <span className="date-dow">{dow(d)}</span>
      <span className="date-day">{dayOfMonth(d)}</span>
    </div>
  );
}

// Tappable upcoming-game row: date, logo, matchup, time and channel.
export default function GameRow({ game, badge }) {
  return (
    <Link to={`/game/${game.id}`} className="game-row">
      <DateStack game={game} />
      <img src={game.opponentLogo} alt="" className="row-logo" />
      <div className="row-main">
        <span className="row-title">{matchup(game)}</span>
        <TimeAndTv time={game.time} tv={game.tv} />
      </div>
      {badge && <span className="pill-badge">{badge}</span>}
      <ChevronRight />
    </Link>
  );
}
