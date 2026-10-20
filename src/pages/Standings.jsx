import { useState } from 'react';
import { useAppData, useFetch } from '../lib/context';
import { WARRIORS_ID } from '../lib/games';
import { daysBetween, shortDate, tipDate, weekday } from '../lib/time';
import { LoadState } from '../components/LoadState';

const CONFERENCES = [
  ['west', 'West'],
  ['east', 'East'],
];

// Playoffs (1–6), Play-in (7–10), Lottery (11–15)
function sections(rows) {
  return [
    { label: 'Playoffs', rows: rows.slice(0, 6) },
    { label: 'Play-in', rows: rows.slice(6, 10) },
    { label: 'Lottery', rows: rows.slice(10) },
  ].filter((s) => s.rows.length);
}

// "2025–26 final · 2026–27 starts Wed" before opening night.
function subtitle(data, schedule, now) {
  if (!data.final) return `${data.season} regular season`;
  const opener = schedule.find((g) => g.seasonType === 'reg');
  if (!opener) return `${data.season} final`;
  const tip = tipDate(opener);
  const days = daysBetween(now, tip);
  if (days < 0) return `${data.season} final`;
  const when = days === 0 ? 'tonight' : days < 7 ? weekday(tip) : shortDate(tip);
  const y = Number(data.season.slice(0, 4)) + 1;
  return `${data.season} final · ${y}–${String((y + 1) % 100).padStart(2, '0')} starts ${when}`;
}

export default function Standings() {
  const { schedule, now } = useAppData();
  const { data, loading, error } = useFetch('/api/standings');
  const [conf, setConf] = useState('west');

  const rows = data?.conferences?.[conf] || [];

  return (
    <main className="page standings-page">
      <div className="page-head">
        <h1 className="page-title">Standings</h1>
        {data?.season && <span className="small muted">{subtitle(data, schedule, now)}</span>}
      </div>

      <div className="segmented" role="tablist" aria-label="Conference">
        {CONFERENCES.map(([id, label]) => (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={conf === id}
            className={`segment ${conf === id ? 'active' : ''}`}
            onClick={() => setConf(id)}
          >
            {label}
          </button>
        ))}
      </div>

      <LoadState loading={loading} error={error} empty={!loading && !error && !rows.length} what="standings" />

      {rows.length > 0 && (
        <div className="standings" role="table" aria-label={`${conf === 'west' ? 'Western' : 'Eastern'} Conference`}>
          <div className="standings-row standings-head" role="row">
            <span className="st-seed" role="columnheader">#</span>
            <span className="st-logo" aria-hidden="true" />
            <span className="st-team" role="columnheader">TEAM</span>
            <span className="st-num" role="columnheader">W</span>
            <span className="st-num" role="columnheader">L</span>
            <span className="st-pct" role="columnheader">PCT</span>
            <span className="st-gb" role="columnheader">GB</span>
          </div>
          {sections(rows).map((s) => (
            <div key={s.label} role="rowgroup">
              <div className="standings-group" role="row">
                <span role="rowheader">{s.label}</span>
              </div>
              {s.rows.map((r, i) => {
                const seed = rows.indexOf(r) + 1;
                const us = r.id === WARRIORS_ID;
                return (
                  <div key={r.id || i} className={`standings-row ${us ? 'us' : ''}`} role="row">
                    <span className="st-seed" role="cell">{seed}</span>
                    <img src={r.logo} alt="" className="st-logo" />
                    <span className="st-team" role="cell">{r.name}</span>
                    <span className="st-num" role="cell">{r.w}</span>
                    <span className="st-num" role="cell">{r.l}</span>
                    <span className="st-pct" role="cell">{r.pct}</span>
                    <span className="st-gb" role="cell">{r.gb === '-' ? '–' : r.gb}</span>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
