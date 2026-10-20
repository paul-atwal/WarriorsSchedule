import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { useAppData, useFetch } from '../lib/context';
import { gameLabel, highlightsUrl, isFinal, matchup, recordText, scoreText, tvText, WARRIORS_LOGO } from '../lib/games';
import { shortDate, tipDate } from '../lib/time';
import { Channel } from '../components/Tv';
import { ChevronLeft, PinIcon, PlayIcon, TvIcon } from '../components/Icons';
import { LoadState } from '../components/LoadState';

function BackLink() {
  const navigate = useNavigate();
  const location = useLocation();
  // Go back to wherever the user came from; deep links fall back to Schedule.
  if (location.key !== 'default') {
    return (
      <button type="button" className="back-link" onClick={() => navigate(-1)}>
        <ChevronLeft />
        Back
      </button>
    );
  }
  return (
    <Link to="/schedule" className="back-link">
      <ChevronLeft />
      Schedule
    </Link>
  );
}

function SeriesRow({ meeting, game, now }) {
  const current = meeting.id === game.id;
  const played = meeting.pts != null && meeting.oppPts != null && isFinal(meeting, now);
  const win = meeting.pts > meeting.oppPts;
  return (
    <div className="series-row">
      <span className="series-date">{shortDate(tipDate(meeting))}</span>
      <span className="series-where">
        <span>{matchup({ ...meeting, opponentShort: game.opponentShort })}</span>
        {meeting.seasonType === 'pre' && <span className="small muted">Preseason</span>}
      </span>
      {played && (
        <span className="result">
          <span className={`wl ${win ? 'win' : 'loss'}`}>{win ? 'W' : 'L'}</span>
          <span className="score-small">{scoreText(meeting.pts, meeting.oppPts)}</span>
        </span>
      )}
      {current && <span className="pill-badge">THIS GAME</span>}
    </div>
  );
}

export default function GamePreview() {
  const { id } = useParams();
  const { schedule, now } = useAppData();
  const { data, loading, error } = useFetch(`/api/game/${id}`);

  if (loading || error || !data) {
    return (
      <main className="page">
        <BackLink />
        <LoadState loading={loading} error={error} what="this game" />
      </main>
    );
  }

  const { game, series, scorers, warriorsRecord, opponentRecord } = data;
  const tip = tipDate(game);
  const final = isFinal(game, now);
  const played = series.filter((m) => m.pts != null && m.oppPts != null && isFinal(m, now));
  const wins = played.filter((m) => m.pts > m.oppPts).length;
  const tv = tvText(game.tv);

  return (
    <main className="page preview-page">
      <BackLink />

      <header className="preview-header">
        <span className="eyebrow gold">{gameLabel(game, schedule)}</span>
        <div className="versus">
          <div className="versus-team">
            <img src={WARRIORS_LOGO} alt="" />
            <span>Warriors</span>
            <span className="small muted">{recordText(warriorsRecord)}</span>
          </div>
          <span className="versus-at">{game.isHome ? 'vs' : '@'}</span>
          <div className="versus-team">
            <img src={game.opponentLogo} alt="" />
            <span>{game.opponentShort}</span>
            <span className="small muted">{recordText(opponentRecord)}</span>
          </div>
        </div>
        <div className="hero-when">
          <h1 className="display-date">{shortDate(tip)}</h1>
          <span className="display-time">{game.time === 'TBD' ? 'Time TBD' : `${game.time} PT`}</span>
        </div>
      </header>

      <section aria-label="Where to watch" className="card facts-card">
        {final ? (
          <a href={highlightsUrl(game)} target="_blank" rel="noopener noreferrer" className="fact-row link">
            <PlayIcon size={16} />
            <span className="fact-label">Final</span>
            <span className="fact-value">Watch highlights</span>
          </a>
        ) : (
          <div className="fact-row">
            <TvIcon />
            <span className="fact-label">On Telus</span>
            {tv ? <span className="fact-value">{tv}</span> : <Channel tv={game.tv} />}
          </div>
        )}
        <div className="fact-row">
          <PinIcon />
          <span className="fact-label">Arena</span>
          <span className="fact-value">{game.arena}</span>
        </div>
      </section>

      <section aria-labelledby="series-h" className="list-section">
        <div className="list-head">
          <h2 id="series-h" className="eyebrow">Season series</h2>
          {played.length > 0 && (
            <span className="small muted">
              Warriors {wins}–{played.length - wins}
            </span>
          )}
        </div>
        {series.map((m) => (
          <SeriesRow key={m.id} meeting={m} game={game} now={now} />
        ))}
      </section>

      <section aria-labelledby="scorers-h" className="card scorers-card">
        <h2 id="scorers-h" className="eyebrow">{game.opponentShort} top scorers</h2>
        {scorers.map((p) => (
          <div key={p.name} className="scorer">
            <span className="avatar">{p.img && <img src={p.img} alt="" />}</span>
            <div className="scorer-main">
              <span className="scorer-name">{p.name}</span>
              <span className="small muted">{p.position}</span>
            </div>
            <div className="scorer-stat">
              <span className="scorer-ppg">{p.ppg.toFixed(1)}</span>
              <span className="stat-label">PTS / GAME</span>
            </div>
          </div>
        ))}
        {!scorers.length && <p className="small muted">Season averages fill in once the regular season starts.</p>}
      </section>
    </main>
  );
}
