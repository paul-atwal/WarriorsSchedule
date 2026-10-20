import { TvIcon, TvOffIcon } from './Icons';

// Telus channel for a game: logo + channel number.
// `variant` "dark" draws the logo black for the gold game-day card.

export function Channel({ tv, size = 'md', variant = 'light' }) {
  return (
    <span className={`channel channel-${size}`}>
      {tv.logo && <img src={tv.logo} alt={tv.name} className={`channel-logo ${variant}`} />}
      {!tv.logo && <span className="channel-name">{tv.name}</span>}
      <span className="channel-number">{tv.number}</span>
    </span>
  );
}

// Compact TV marker for rows: the channel, a crossed-out TV when it isn't on
// Telus (NBA TV-only counts as not on), or a TV with "TBA" before listings are out.
export function TvMark({ tv }) {
  if (tv?.status === 'on') return <Channel tv={tv} size="sm" />;
  if (tv?.status === 'none') return <TvOffIcon />;
  return (
    <span className="tv-tba">
      <TvIcon size={17} />
      TBA
    </span>
  );
}

// Inline form used in game rows: "7:00 PM · [SN1] 912"
export function TimeAndTv({ time, tv, prefix = '' }) {
  return (
    <span className="row-sub">
      <span>
        {prefix}
        {time === 'TBD' ? 'Time TBD' : time} ·
      </span>
      <TvMark tv={tv} />
    </span>
  );
}
