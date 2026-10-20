import { tvText } from '../lib/games';

// Telus channel for a game: logo + channel number, "No TV", or "TV TBA".
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

// Inline form used in game rows: "7:00 PM · No TV" or "7:00 PM · [SN1] 912"
export function TimeAndTv({ time, tv }) {
  const text = tvText(tv);
  return (
    <span className="row-sub">
      <span>
        {time === 'TBD' ? 'Time TBD' : time} ·{text ? ` ${text}` : ''}
      </span>
      {!text && <Channel tv={tv} size="sm" />}
    </span>
  );
}
