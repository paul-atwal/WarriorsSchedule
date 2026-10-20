import { createContext, useContext, useEffect, useState } from 'react';

export const AppDataContext = createContext(null);

// { schedule, loading, error, now, scoresOn, toggleScores }
export const useAppData = () => useContext(AppDataContext);

export function useFetch(url) {
  // Keyed by url so a new url reads as loading without resetting state in the effect.
  const [state, setState] = useState({ url: null, data: null, error: null });
  useEffect(() => {
    let cancelled = false;
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(res.status === 404 ? 'Not found' : 'Could not load data');
        return res.json();
      })
      .then((data) => !cancelled && setState({ url, data, error: null }))
      .catch((error) => !cancelled && setState({ url, data: null, error }));
    return () => {
      cancelled = true;
    };
  }, [url]);
  const current = state.url === url;
  return { data: current ? state.data : null, error: current ? state.error : null, loading: !current };
}

// Fetches a live/final score only while `enabled`, refreshing during a live game.
export function useScore(gameId, enabled, live) {
  const [score, setScore] = useState(null);
  useEffect(() => {
    if (!enabled || !gameId) return undefined;
    let cancelled = false;
    const load = () =>
      fetch(`/api/score/${gameId}`)
        .then((res) => (res.ok ? res.json() : Promise.reject(new Error('unavailable'))))
        .then((data) => !cancelled && setScore(data))
        .catch(() => !cancelled && setScore((s) => s || { error: true }));
    load();
    const timer = live ? setInterval(load, 30000) : null;
    return () => {
      cancelled = true;
      if (timer) clearInterval(timer);
    };
  }, [gameId, enabled, live]);
  return enabled ? score : null;
}
