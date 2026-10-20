import { dateKey, monthDay, tipDate } from './time';

const HOUR = 3600000;
// A game is treated as finished this long after tip-off, even before the
// daily data update records the result.
const GAME_LENGTH = 3 * HOUR;
// How long the "Highlights ready" card stays on top of Home after a game.
const FINAL_ON_TOP = 12 * HOUR;

export function phase(game, now) {
  const tip = tipDate(game);
  if (game.status === 'post' || game.wl) return 'final';
  if (now - tip >= GAME_LENGTH) return 'final';
  if (now >= tip || game.status === 'in') return 'live';
  return 'upcoming';
}

export const isFinal = (game, now) => phase(game, now) === 'final';

// What Home shows: the card on top, the last game below it, then the next few.
export function homeGames(schedule, now) {
  const hero = schedule.find((g) => !isFinal(g, now) || now - tipDate(g) < FINAL_ON_TOP) || null;
  let heroState = null;
  if (hero) {
    const p = phase(hero, now);
    if (p === 'final') heroState = 'final';
    else if (p === 'live') heroState = 'live';
    else heroState = dateKey(tipDate(hero)) === dateKey(now) ? 'tonight' : 'next';
  }
  const heroIndex = hero ? schedule.indexOf(hero) : schedule.length;
  const last = [...schedule.slice(0, heroIndex)].reverse().find((g) => isFinal(g, now)) || null;
  const comingUp = schedule.slice(heroIndex + 1).filter((g) => !isFinal(g, now)).slice(0, 4);
  return { hero, heroState, last, comingUp };
}

export const matchup = (game) => `${game.isHome ? 'vs' : '@'} ${game.opponentShort}`;

export function isOpeningNight(game, schedule) {
  return game.seasonType === 'reg' && schedule.find((g) => g.seasonType === 'reg')?.id === game.id;
}

export function gameLabel(game, schedule) {
  if (isOpeningNight(game, schedule)) return 'Opening night';
  if (game.seasonType === 'pre') return 'Preseason';
  if (game.seasonType === 'post') return 'Playoffs';
  return game.isHome ? 'Home game' : 'Road game';
}

export function highlightsUrl(game) {
  const d = tipDate(game);
  const q = `Warriors ${game.opponentShort} highlights ${monthDay(d)} ${dateKey(d).slice(0, 4)}`;
  return `https://www.youtube.com/results?search_query=${encodeURIComponent(q)}`;
}

export function tvText(tv) {
  if (!tv || tv.status === 'tba') return 'TV TBA';
  if (tv.status === 'none') return 'No TV';
  return null;
}

export const scoreText = (pts, oppPts) => `${pts}–${oppPts}`;

export function seasonLabel(schedule) {
  if (!schedule.length) return '';
  const y = Number(dateKey(tipDate(schedule[0])).slice(0, 4));
  return `${y}–${String((y + 1) % 100).padStart(2, '0')} season`;
}

export const WARRIORS_LOGO = 'https://a.espncdn.com/i/teamlogos/nba/500/gs.png';
