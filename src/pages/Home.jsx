import { Link } from 'react-router-dom';
import { useAppData } from '../lib/context';
import { highlightsUrl, homeGames, matchup, scoreText, seasonLabel, WARRIORS_LOGO } from '../lib/games';
import { shortDate, tipDate } from '../lib/time';
import HeroCard from '../components/HeroCard';
import GameRow from '../components/GameRow';
import { EyeIcon, EyeOffIcon, PlayIcon } from '../components/Icons';
import { LoadState } from '../components/LoadState';

function ScoresToggle() {
  const { scoresOn, toggleScores } = useAppData();
  return (
    <button
      type="button"
      className={`scores-toggle ${scoresOn ? 'on' : ''}`}
      aria-label={scoresOn ? 'Scores shown. Hide all scores' : 'Scores hidden. Show all scores'}
      aria-pressed={scoresOn}
      onClick={toggleScores}
    >
      {scoresOn ? <EyeIcon /> : <EyeOffIcon />}
      <span>{scoresOn ? 'Scores on' : 'Scores off'}</span>
    </button>
  );
}

function LastGame({ game }) {
  const { scoresOn } = useAppData();
  const hasScore = game.pts != null && game.oppPts != null;
  return (
    <section aria-labelledby="last-h" className="card">
      <div className="card-head">
        <h2 id="last-h" className="eyebrow">Last game</h2>
        {game.seasonType !== 'reg' && (
          <span className="small muted">{game.seasonType === 'pre' ? 'Preseason' : 'Playoffs'}</span>
        )}
      </div>
      <div className="hero-row">
        <img src={game.opponentLogo} alt="" className="last-logo" />
        <div className="hero-row-main">
          <span className="last-title">{matchup(game)}</span>
          <span className="row-sub">
            {shortDate(tipDate(game))} · {game.arena}
          </span>
        </div>
        {scoresOn && hasScore ? (
          <span className="result">
            <span className={`wl ${game.wl === 'W' ? 'win' : 'loss'}`}>{game.wl}</span>
            <span className="score-small">{scoreText(game.pts, game.oppPts)}</span>
          </span>
        ) : (
          <span className="hidden-chip">
            <EyeOffIcon size={14} />
            Score hidden
          </span>
        )}
      </div>
      <a href={highlightsUrl(game)} target="_blank" rel="noopener noreferrer" className="button raised big">
        <span className="play-disc">
          <PlayIcon />
        </span>
        Watch highlights
      </a>
    </section>
  );
}

export default function Home() {
  const { schedule, loading, error, now } = useAppData();
  const { hero, heroState, last, comingUp } = homeGames(schedule, now);

  return (
    <main className="page">
      <header className="home-header">
        <div className="brand">
          <img src={WARRIORS_LOGO} alt="" />
          <div className="brand-text">
            <span className="brand-name">Warriors</span>
            <span className="small muted">{seasonLabel(schedule)}</span>
          </div>
        </div>
        <ScoresToggle />
      </header>

      <LoadState loading={loading} error={error} empty={!schedule.length} />

      {hero && <HeroCard game={hero} state={heroState} />}
      {last && <LastGame game={last} />}

      {comingUp.length > 0 && (
        <section aria-labelledby="up-h" className="list-section">
          <div className="list-head">
            <h2 id="up-h" className="eyebrow">Coming up</h2>
            <Link to="/schedule" className="text-link">
              Full schedule
            </Link>
          </div>
          {comingUp.map((g) => (
            <GameRow key={g.id} game={g} />
          ))}
        </section>
      )}
    </main>
  );
}
