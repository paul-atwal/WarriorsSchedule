import { useEffect, useMemo, useState } from 'react';
import { AppDataContext, useFetch } from './context';

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
  const { data: records } = useFetch('/api/records');
  const [offset] = useState(clockOffset);
  const [now, setNow] = useState(() => new Date(Date.now() + offset));

  // The Home card changes with the clock (countdown, tonight, live, final).
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date(Date.now() + offset)), 30000);
    return () => clearInterval(timer);
  }, [offset]);

  const value = useMemo(
    () => ({ schedule: data || [], records: records || {}, loading, error, now }),
    [data, records, loading, error, now],
  );
  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}
