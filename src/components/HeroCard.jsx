import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAppData, useScore } from '../lib/context';
import { countdownLabel, shortDate, tipDate, tipOffIn } from '../lib/time';
import { highlightsUrl, isOpeningNight, matchup, tvText, WARRIORS_LOGO } from '../lib/games';
import { Channel } from './Tv';
import { EyeOffIcon, PinIcon, PlayIcon, TvIcon } from './Icons';

const title = (game) => `Warriors ${game.isHome ? 'vs' : '@'} ${game.opponentShort}`;
const place = (game) => [game.arena, game.city].filter(Boolean).join(', ');

function TvLine({ tv, variant }) {
  const text = tvText(tv);
  if (text) {
    return (
      <span className="tv-text">
        <TvIcon />
        {text === 'No TV' ? 'Not on Telus TV' : 'TV channel TBA'}
      </span>
    );
  }
  return <Channel tv={tv} variant={variant} />;
}

// The score, only ever rendered after the viewer asks for it.
function ScoreReveal({ game, live, onHide }) {
  const fromData = game.pts != null && game.oppPts != null;
  const fetched = useScore(game.id, !fromData, live);
  const score = fromData ? { pts: game.pts, oppPts: game.oppPts, state: 'post' } : fetched;

  if (!score) return <p className="score-reveal muted">Loading score…</p>;
  if (score.error || score.pts == null) return <p className="score-reveal muted">Score not available yet.</p>;

  const final = score.state === 'post';
  const win = score.pts > score.oppPts;
  return (
    <div className="score-reveal">
      <div className="score-line">
        <span className="score-team">GSW</span>
        <span className="score-num">{score.pts}</span>
        <span className="score-dash">–</span>
        <span className="score-num">{score.oppPts}</span>
        <span className="score-team">{game.opponentAbbr}</span>
      </div>
      <div className="score-meta">
        {final ? (
          <span className={`wl ${win ? 'win' : 'loss'}`}>{win ? 'W' : 'L'}</span>
        ) : (
          <span>{score.detail || 'Live'}</span>
        )}
        {onHide && (
          <button type="button" className="link-button" onClick={onHide}>
            Hide score
          </button>
        )}
      </div>
    </div>
  );
}

function NextCard({ game, schedule, now }) {
  const tip = tipDate(game);
  const label = isOpeningNight(game, schedule) ? 'Next game · Opening night' : 'Next game';
  return (
    <section aria-labelledby="next-h" className="card hero">
      <div className="card-head">
        <h2 id="next-h" className="eyebrow gold">{label}</h2>
        <span className="pill gold">{countdownLabel(now, tip)}</span>
      </div>
      <div className="versus">
        <div className="versus-team">
          <img src={WARRIORS_LOGO} alt="" />
          <span>Warriors</span>
        </div>
        <div className="versus-at">{game.isHome ? 'vs' : '@'}</div>
        <div className="versus-team">
          <img src={game.opponentLogo} alt="" />
          <span>{game.opponentShort}</span>
        </div>
      </div>
      <div className="hero-when">
        <span className="display-date">{shortDate(tip)}</span>
        <span className="display-time">{game.time === 'TBD' ? 'Time TBD' : `${game.time} PT`}</span>
      </div>
      <div className="hero-facts">
        <div className="fact">
          <TvLine tv={game.tv} />
        </div>
        <div className="fact">
          <PinIcon />
          <span>{place(game)}</span>
        </div>
      </div>
      <Link to={`/game/${game.id}`} className="button gold">
        Game preview
      </Link>
    </section>
  );
}

function TonightCard({ game, now }) {
  const tip = tipDate(game);
  return (
    <section aria-label="Tonight's game" className="card hero tonight">
      <div className="card-head">
        <span className="eyebrow">Tonight</span>
        <span className="pill navy">{tipOffIn(now, tip)}</span>
      </div>
      <div className="tonight-main">
        <div className="tonight-logos">
          <span className="logo-disc">
            <img src={WARRIORS_LOGO} alt="" />
          </span>
          <span className="tonight-at">{game.isHome ? 'vs' : '@'}</span>
          <span className="logo-disc">
            <img src={game.opponentLogo} alt="" />
          </span>
        </div>
        <div className="tonight-when">
          <span className="tonight-time">{game.time}</span>
          <span className="tonight-sub">
            {matchup(game)} · {shortDate(tip)}
          </span>
        </div>
      </div>
      <div className="fact strong">
        <TvLine tv={game.tv} variant="dark" />
      </div>
      <Link to={`/game/${game.id}`} className="button navy">
        Game preview
      </Link>
    </section>
  );
}

function LiveCard({ game, scoresOn }) {
  const [shown, setShown] = useState(false);
  const reveal = scoresOn || shown;
  return (
    <section aria-label="Game in progress" className="card hero">
      <div className="live-head">
        <span className="live-dot" />
        <span className="eyebrow gold">In progress</span>
      </div>
      <div className="hero-row">
        <img src={game.opponentLogo} alt="" className="hero-row-logo" />
        <div className="hero-row-main">
          <span className="hero-row-title">{title(game)}</span>
          <span className="row-sub">
            <span>Tipped off {game.time} ·{tvText(game.tv) ? ` ${tvText(game.tv)}` : ''}</span>
            {!tvText(game.tv) && <Channel tv={game.tv} size="sm" />}
          </span>
        </div>
      </div>
      {reveal ? (
        <ScoreReveal game={game} live onHide={scoresOn ? null : () => setShown(false)} />
      ) : (
        <button type="button" className="button dashed" onClick={() => setShown(true)}>
          <EyeOffIcon />
          Show live score
        </button>
      )}
    </section>
  );
}

function FinalCard({ game, scoresOn }) {
  const [shown, setShown] = useState(false);
  const reveal = scoresOn || shown;
  return (
    <section aria-label="Final, highlights ready" className="card hero">
      <div className="card-head">
        <span className="eyebrow light">Final · Highlights ready</span>
        <span className="small muted">{shortDate(tipDate(game))}</span>
      </div>
      <div className="hero-row">
        <img src={game.opponentLogo} alt="" className="hero-row-logo" />
        <div className="hero-row-main">
          <span className="hero-row-title">{title(game)}</span>
          <span className="row-sub">{game.arena}</span>
        </div>
      </div>
      <a href={highlightsUrl(game)} target="_blank" rel="noopener noreferrer" className="button gold big">
        <PlayIcon size={16} />
        Watch highlights
      </a>
      {reveal ? (
        <ScoreReveal game={game} onHide={scoresOn ? null : () => setShown(false)} />
      ) : (
        <button type="button" className="link-button centered" onClick={() => setShown(true)}>
          Show final score
        </button>
      )}
    </section>
  );
}

export default function HeroCard({ game, state }) {
  const { schedule, now, scoresOn } = useAppData();
  if (state === 'tonight') return <TonightCard game={game} now={now} />;
  if (state === 'live') return <LiveCard key={game.id} game={game} scoresOn={scoresOn} />;
  if (state === 'final') return <FinalCard key={game.id} game={game} scoresOn={scoresOn} />;
  return <NextCard game={game} schedule={schedule} now={now} />;
}
