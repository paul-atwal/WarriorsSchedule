import { NavLink } from 'react-router-dom';
import { useAppData, useScore } from '../lib/context';
import { highlightsUrl, isFinal, matchup, phase, scoreText } from '../lib/games';
import { monthDay, monthName, tipDate } from '../lib/time';
import GameRow, { DateStack } from '../components/GameRow';
import { PlayIcon } from '../components/Icons';
import { LoadState } from '../components/LoadState';

function groupByMonth(games, withSeasonType) {
  const groups = [];
  for (const g of games) {
    let name = monthName(tipDate(g));
    if (withSeasonType && g.seasonType === 'pre') name = `Preseason · ${name}`;
    if (withSeasonType && g.seasonType === 'post') name = `Playoffs · ${name}`;
    const last = groups[groups.length - 1];
    if (last && last.name === name) last.games.push(g);
    else groups.push({ name, games: [g] });
  }
  return groups;
}

function ResultRow({ game }) {
  const hasScore = game.pts != null && game.oppPts != null;
  // Finished since the last data update: ask ESPN for the result.
  const live = useScore(game.id, !hasScore, false);
  const pts = hasScore ? game.pts : live?.state === 'post' ? live.pts : null;
  const oppPts = hasScore ? game.oppPts : live?.state === 'post' ? live.oppPts : null;
  const win = pts > oppPts;

  return (
    <div className="game-row result-row">
      <DateStack game={game} />
      <img src={game.opponentLogo} alt="" className="row-logo" />
      <div className="row-main">
        <span className="row-title">{matchup(game)}</span>
        {pts != null && (
          <span className="result">
            <span className={`wl ${win ? 'win' : 'loss'}`}>{win ? 'W' : 'L'}</span>
            <span className="score-small">{scoreText(pts, oppPts)}</span>
          </span>
        )}
      </div>
      <a
        href={highlightsUrl(game)}
        target="_blank"
        rel="noopener noreferrer"
        className="pill-button"
        aria-label={`Watch highlights: ${matchup(game)}, ${monthDay(tipDate(game))}`}
      >
        <PlayIcon />
        Highlights
      </a>
    </div>
  );
}

export default function Schedule({ previous = false }) {
  const { schedule, loading, error, now } = useAppData();
  const games = previous
    ? schedule.filter((g) => isFinal(g, now)).reverse()
    : schedule.filter((g) => !isFinal(g, now));
  const groups = groupByMonth(games, previous);
  const nextId = !previous && games[0]?.id;

  return (
    <main className="page schedule-page">
      <div className="schedule-top">
        <h1 className="page-title">Schedule</h1>
        <div className="segmented" aria-label="Games">
          <NavLink to="/schedule" end className="segment">
            Upcoming
          </NavLink>
          <NavLink to="/schedule/previous" className="segment">
            Previous
          </NavLink>
        </div>
      </div>

      <LoadState loading={loading} error={error} empty={!schedule.length} />
      {!loading && !error && schedule.length > 0 && !games.length && (
        <p className="load-state">{previous ? 'No games played yet.' : 'No games left this season.'}</p>
      )}

      {groups.map((m) => (
        <section key={m.name} className="month">
          <h2 className="month-head eyebrow">{m.name}</h2>
          {m.games.map((g) =>
            previous ? (
              <ResultRow key={g.id} game={g} />
            ) : (
              <GameRow
                key={g.id}
                game={g}
                badge={phase(g, now) === 'live' ? 'LIVE' : g.id === nextId ? 'NEXT' : null}
              />
            ),
          )}
        </section>
      ))}
    </main>
  );
}
