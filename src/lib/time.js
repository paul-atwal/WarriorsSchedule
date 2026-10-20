// All dates in the app are shown in Pacific time, where the Warriors play.
export const TZ = 'America/Los_Angeles';

const fmt = (opts) => new Intl.DateTimeFormat('en-US', { timeZone: TZ, ...opts });
const dowFmt = fmt({ weekday: 'short' });
const dayFmt = fmt({ day: 'numeric' });
const monthFmt = fmt({ month: 'long' });
const shortDateFmt = fmt({ weekday: 'short', month: 'short', day: 'numeric' });
const monthDayFmt = fmt({ month: 'short', day: 'numeric' });
const keyFmt = new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' });

export const tipDate = (game) => new Date(game.tipUtc);

export const dow = (d) => dowFmt.format(d).toUpperCase();
export const dayOfMonth = (d) => dayFmt.format(d);
export const monthName = (d) => monthFmt.format(d);
export const shortDate = (d) => shortDateFmt.format(d); // "Wed, Oct 21"
export const monthDay = (d) => monthDayFmt.format(d); // "Oct 21"
export const weekday = (d) => dowFmt.format(d); // "Wed"
export const dateKey = (d) => keyFmt.format(d); // "2026-10-21" in PT

// Calendar days between two instants, in Pacific time.
export function daysBetween(from, to) {
  const [a, b] = [dateKey(from), dateKey(to)].map((k) => {
    const [y, m, d] = k.split('-').map(Number);
    return Date.UTC(y, m - 1, d);
  });
  return Math.round((b - a) / 86400000);
}

export function countdownLabel(now, tip) {
  const days = daysBetween(now, tip);
  if (days <= 0) return 'Today';
  if (days === 1) return 'Tomorrow';
  return `In ${days} days`;
}

export function tipOffIn(now, tip) {
  const mins = Math.max(0, Math.round((tip - now) / 60000));
  if (mins < 1) return 'Tip-off soon';
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return `Tip-off in ${h ? `${h}h ` : ''}${m}m`;
}

export function timeAgo(now, iso) {
  const mins = Math.max(0, Math.round((now - new Date(iso)) / 60000));
  if (mins < 60) return `${Math.max(mins, 1)}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  if (days < 7) return `${days}d ago`;
  return monthDay(new Date(iso));
}
