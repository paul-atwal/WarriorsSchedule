import { useAppData, useFetch } from '../lib/context';
import { homeGames } from '../lib/games';
import { dateKey, monthDay, timeAgo, tipDate, weekday } from '../lib/time';
import { ChevronRight } from '../components/Icons';
import { LoadState } from '../components/LoadState';

const CURRY_HEADSHOT = 'https://a.espncdn.com/i/headshots/nba/players/full/3975.png';

function statusBadge(status) {
  const s = (status || '').toLowerCase();
  if (s === 'out') return { label: 'OUT', tone: 'out' };
  if (s === 'day-to-day') return { label: 'DAY-TO-DAY', tone: 'dtd' };
  return { label: (status || 'Unknown').toUpperCase(), tone: 'dtd' };
}

function returnText(injury, now) {
  if (!injury.returnDate) return null;
  const d = new Date(`${injury.returnDate}T12:00:00`);
  if (dateKey(d) <= dateKey(now)) return null;
  return `est. return ${monthDay(d)}`;
}

function CurryCard({ injury, updated }) {
  const badge = injury ? statusBadge(injury.status) : { label: 'NO INJURY', tone: 'ok' };
  return (
    <section aria-labelledby="curry-h" className="card">
      <div className="card-head">
        <h2 id="curry-h" className="eyebrow gold">Curry status</h2>
        {(injury?.updated || updated) && (
          <span className="small muted">Updated {monthDay(new Date(injury?.updated || updated))}</span>
        )}
      </div>
      <div className="curry-row">
        <span className="avatar big">
          <img src={injury?.img || CURRY_HEADSHOT} alt="" />
        </span>
        <div className="curry-main">
          <span className="curry-name">Stephen Curry</span>
          <span className="curry-status">
            <span className={`status-badge ${badge.tone}`}>{badge.label}</span>
            {injury && <span className="small light">{injury.injury}</span>}
          </span>
        </div>
      </div>
      <p className="curry-note">
        {injury ? injury.comment : 'Not on the injury report. Expected to be available.'}
      </p>
    </section>
  );
}

export default function News() {
  const { schedule, now } = useAppData();
  const { data, loading, error } = useFetch('/api/news');
  const { hero } = homeGames(schedule, now);

  if (loading || error || !data) {
    return (
      <main className="page">
        <h1 className="page-title">News</h1>
        <LoadState loading={loading} error={error} what="news" />
      </main>
    );
  }

  const curry = data.injuries.find((i) => i.athleteId === data.curryId);
  const others = data.injuries.filter((i) => i !== curry);

  return (
    <main className="page news-page">
      <h1 className="page-title">News</h1>

      <CurryCard injury={curry} updated={data.updated} />

      <section aria-labelledby="inj-h" className="list-section">
        <div className="list-head">
          <h2 id="inj-h" className="eyebrow">Injury report</h2>
          {hero && (
            <span className="small muted">
              Next: {weekday(tipDate(hero))} {hero.isHome ? 'vs' : '@'} {hero.opponentAbbr}
            </span>
          )}
        </div>
        {others.map((p) => {
          const badge = statusBadge(p.status);
          const back = returnText(p, now);
          return (
            <div key={p.name} className="injury-row">
              <span className="avatar">{p.img && <img src={p.img} alt="" />}</span>
              <div className="row-main">
                <span className="row-title">{p.name}</span>
                <span className="row-sub">{[p.injury, back].filter(Boolean).join(' · ')}</span>
              </div>
              <span className={`status-badge ${badge.tone}`}>{badge.label}</span>
            </div>
          );
        })}
        {!others.length && <p className="empty-row">No other Warriors on the injury report.</p>}
      </section>

      <section aria-labelledby="news-h" className="list-section">
        <div className="list-head">
          <h2 id="news-h" className="eyebrow">Latest</h2>
        </div>
        {data.articles.map((a) => (
          <a key={a.url} href={a.url} target="_blank" rel="noopener noreferrer" className="news-row">
            <div className="row-main">
              <span className="news-headline">{a.headline}</span>
              <span className="small muted">ESPN · {timeAgo(now, a.published)}</span>
            </div>
            <ChevronRight />
          </a>
        ))}
        {!data.articles.length && <p className="empty-row">No Warriors stories right now.</p>}
      </section>
    </main>
  );
}
