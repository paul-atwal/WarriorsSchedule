export function LoadState({ loading, error, empty, what = 'the schedule' }) {
  if (loading) return <p className="load-state">Loading…</p>;
  if (error) return <p className="load-state">Couldn’t load {what}. Check your connection and try again.</p>;
  if (empty) return <p className="load-state">No games to show yet.</p>;
  return null;
}
