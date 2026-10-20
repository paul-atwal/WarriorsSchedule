import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAppData, useScore } from '../lib/context';
import { highlightsUrl, homeGames, matchup, scoreText, seasonLabel, WARRIORS_LOGO } from '../lib/games';
import { shortDate, tipDate } from '../lib/time';
import HeroCard from '../components/HeroCard';
import GameRow from '../components/GameRow';
import { EyeIcon, EyeOffIcon, PlayIcon } from '../components/Icons';
import { LoadState } from '../components/LoadState';

function LastGame({ game }) {
  // Hidden until the viewer taps the eye.
  const [shown, setShown] = useState(false);
  const fromData = game.pts != null && game.oppPts != null;
  // Finished since the last data update: ask ESPN, but only once revealed.
  const live = useScore(game.id, shown && !fromData, false);
  const pts = fromData ? game.pts : live?.state === 'post' ? live.pts : null;
  const oppPts = fromData ? game.oppPts : live?.state === 'post' ? live.oppPts : null;
  const hasScore = pts != null && oppPts != null;
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
        {shown && hasScore && (
          <span className="result">
            <span className={`wl ${pts > oppPts ? 'win' : 'loss'}`}>{pts > oppPts ? 'W' : 'L'}</span>
            <span className="score-last">{scoreText(pts, oppPts)}</span>
          </span>
        )}
        {shown && !hasScore && <span className="small muted">{live ? 'Not available' : 'Loading…'}</span>}
        <button
          type="button"
          className="icon-button"
          aria-pressed={shown}
          aria-label={shown ? 'Hide score' : 'Show score'}
          onClick={() => setShown((s) => !s)}
        >
          {shown ? <EyeIcon size={20} /> : <EyeOffIcon size={20} />}
        </button>
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
      </header>

      <LoadState loading={loading} error={error} empty={!schedule.length} />

      {hero && <HeroCard game={hero} state={heroState} />}
      {last && <LastGame key={last.id} game={last} />}

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
