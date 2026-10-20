import { useCallback, useEffect, useMemo, useState } from 'react';
import { AppDataContext, useFetch } from './context';

const SCORES_KEY = 'warriors.scoresOn';

function readScoresPref() {
  try {
    return localStorage.getItem(SCORES_KEY) === '1';
  } catch {
    return false;
  }
}

// Dev only: `?now=2026-10-21T18:00:00-07:00` pretends it's that moment, to
// check the Home card's game-day states.
function clockOffset() {
  if (!import.meta.env.DEV) return 0;
  const fake = new URLSearchParams(window.location.search).get('now');
  const t = fake ? Date.parse(fake) : NaN;
  return Number.isNaN(t) ? 0 : t - Date.now();
}

export default function AppData({ children }) {
  const { data, loading, error } = useFetch('/api/schedule');
  const [offset] = useState(clockOffset);
  const [now, setNow] = useState(() => new Date(Date.now() + offset));
  const [scoresOn, setScoresOn] = useState(readScoresPref);

  // The Home card changes with the clock (countdown, tonight, live, final).
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date(Date.now() + offset)), 30000);
    return () => clearInterval(timer);
  }, [offset]);

  const toggleScores = useCallback(() => {
    setScoresOn((on) => {
      try {
        localStorage.setItem(SCORES_KEY, on ? '0' : '1');
      } catch {
        // private mode: keep the choice for this visit only
      }
      return !on;
    });
  }, []);

  const value = useMemo(
    () => ({ schedule: data || [], loading, error, now, scoresOn, toggleScores }),
    [data, loading, error, now, scoresOn, toggleScores],
  );
  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}
