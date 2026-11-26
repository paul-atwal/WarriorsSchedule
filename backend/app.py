import json
import os
import sys
import time
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_data import get_standings as fetch_live_standings, parse_utc  # noqa: E402

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
ESPN_SUMMARY = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary'
WARRIORS_ESPN_ID = '9'


def load(name, default):
    try:
        with open(os.path.join(DATA_DIR, name)) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {name}: {e}")
        return default


# Standings and records change after every game, so they come from ESPN live
# rather than the once-a-day data files. Cached briefly per instance (and by
# the CDN via Cache-Control); the data files are only a fallback.
LIVE_TTL = 300
_live = {"at": 0, "records": None, "standings": None}


def saved_records():
    details = load('team_details.json', {})
    records = {k: v.get('record', '0-0') for k, v in details.items() if not k.startswith('_')}
    records[WARRIORS_ESPN_ID] = details.get('_warriors', {}).get('record', '0-0')
    return records


def live_data():
    """(records, standings), live from ESPN when possible."""
    if time.time() - _live["at"] > LIVE_TTL:
        schedule = load('schedule.json', [])
        if schedule:
            season_year = parse_utc(schedule[-1]['tipUtc']).year
            records, standings = fetch_live_standings(season_year)
            if records and standings:
                _live.update(at=time.time(), records=records, standings=standings)
            else:  # ESPN failed: serve what we have, try again in a minute
                _live["at"] = time.time() - LIVE_TTL + 60
    if _live["standings"]:
        return _live["records"], _live["standings"]
    return saved_records(), load('standings.json', None)


def cached(response, seconds=LIVE_TTL):
    response.headers['Cache-Control'] = f'public, max-age=60, s-maxage={seconds}, stale-while-revalidate=600'
    return response


@app.route('/api/schedule')
def get_schedule():
    """The whole season, oldest first. The client decides what's next/last
    from the current time, so this never goes stale between data updates."""
    return jsonify(load('schedule.json', []))


@app.route('/api/game/<game_id>')
def get_game(game_id):
    schedule = load('schedule.json', [])
    game = next((g for g in schedule if str(g['id']) == str(game_id)), None)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    details = load('team_details.json', {})
    opponent = details.get(str(game['opponentId']), {})
    records, _ = live_data()

    # Every meeting with this opponent this season, preseason included
    series = [
        {k: g[k] for k in ('id', 'tipUtc', 'date', 'isHome', 'arena', 'seasonType', 'status', 'wl', 'pts', 'oppPts')}
        for g in schedule if g['opponentId'] == game['opponentId']
    ]

    return jsonify({
        "game": game,
        "warriorsRecord": records.get(WARRIORS_ESPN_ID, '0-0'),
        "opponentRecord": records.get(str(game['opponentId']), opponent.get('record', '0-0')),
        "scorers": opponent.get('scorers', []),
        "series": series,
    })


@app.route('/api/records')
def get_records():
    """Current-season record ("W-L") for every team, keyed by ESPN team id."""
    records, _ = live_data()
    return cached(jsonify(records))


@app.route('/api/standings')
def get_standings():
    _, standings = live_data()
    return cached(jsonify(standings or {"season": "", "final": False, "conferences": {"west": [], "east": []}}))


@app.route('/api/news')
def get_news():
    return jsonify(load('news.json', {"injuries": [], "articles": []}))


@app.route('/api/score/<game_id>')
def get_score(game_id):
    """Live or final score straight from ESPN. Only called when the user
    explicitly asks to see a score."""
    try:
        res = requests.get(ESPN_SUMMARY, params={'event': game_id}, timeout=10)
        res.raise_for_status()
        comp = res.json()['header']['competitions'][0]
    except Exception as e:
        print(f"Error fetching score for {game_id}: {e}")
        return jsonify({"error": "Score unavailable"}), 502

    status = comp.get('status', {}).get('type', {})
    us = next((c for c in comp['competitors'] if c['team']['id'] == WARRIORS_ESPN_ID), {})
    them = next((c for c in comp['competitors'] if c['team']['id'] != WARRIORS_ESPN_ID), {})

    def pts(c):
        try:
            return int(c.get('score'))
        except (TypeError, ValueError):
            return None

    return jsonify({
        "state": status.get('state'),  # pre | in | post
        "detail": status.get('shortDetail'),
        "pts": pts(us),
        "oppPts": pts(them),
        "fetched": datetime.now(timezone.utc).isoformat(),
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
