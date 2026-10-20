"""Builds the static data files the app serves.

Sources:
- ESPN site API: schedule (preseason, regular season, playoffs), standings,
  opponent scoring leaders, Warriors injuries and Warriors news.
- Gracenote TV listings: the TELUS Optik TV lineup for Surrey, BC, to find which
  channel carries each game. Listings run about two weeks ahead.

Runs daily from GitHub Actions; writes backend/data/{schedule,standings,team_details,news}.json.
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone

import requests

try:
    from zoneinfo import ZoneInfo
    PACIFIC_TZ = ZoneInfo("America/Los_Angeles")
except Exception:
    PACIFIC_TZ = timezone(timedelta(hours=-8))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

ESPN_SITE = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba'
ESPN_STANDINGS = 'https://site.api.espn.com/apis/v2/sports/basketball/nba/standings'
ESPN_CORE = 'https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba'
WARRIORS_ESPN_ID = '9'
CURRY_ESPN_ID = '3975'

# TELUS Optik TV - Digital, Vancouver/Whistler headend (Surrey, BC)
GRACENOTE_GRID = 'https://tvlistings.gracenote.com/api/grid'
TELUS_LINEUP = {
    'lineupId': 'CAN-0009972-DEFAULT',
    'headendId': '0009972',
    'country': 'CAN',
    'device': 'X',
    'postalCode': 'V3T1V8',
}
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/130.0 Safari/537.36',
    'Referer': 'https://tvlistings.gracenote.com/grid-affiliates.html?aid=orbebb',
    'Accept': 'application/json, text/plain, */*',
}

# Friendly names for the channels a Warriors game can land on. Anything else
# falls back to Gracenote's affiliate name or call sign.
CHANNEL_NAMES = {
    'SN1': 'Sportsnet One',
    'SNP': 'Sportsnet Pacific',
    'SNW': 'Sportsnet West',
    'SNO': 'Sportsnet Ontario',
    'SNE': 'Sportsnet East',
    'SN360': 'Sportsnet 360',
    'SP4K': 'Sportsnet 4K',
    'TSN': 'TSN',
    'TSN1': 'TSN1',
    'TSN2': 'TSN2',
    'TSN3': 'TSN3',
    'TSN4': 'TSN4',
    'TSN5': 'TSN5',
}
# Channels to check when deciding whether a time slot is listed yet.
REFERENCE_CHANNELS = ('SN1HD', 'SNPHD', 'TSNHD')


def get_json(url, params=None, headers=None, retries=2):
    for attempt in range(retries + 1):
        try:
            res = requests.get(url, params=params, headers=headers or BROWSER_HEADERS, timeout=30)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            status = getattr(getattr(e, 'response', None), 'status_code', None)
            if attempt == retries or (status and 400 <= status < 500):
                raise
            print(f"  retrying {url}: {e}")
            time.sleep(1.5)


def load_json(name, default):
    try:
        with open(os.path.join(DATA_DIR, name)) as f:
            return json.load(f)
    except Exception:
        return default


def write_json(name, data):
    with open(os.path.join(DATA_DIR, name), 'w') as f:
        json.dump(data, f, indent=2)


def parse_utc(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def to_utc_str(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def tidy_venue(name):
    # ESPN lists Crypto.com Arena as "crypto.com Arena"
    return name[:1].upper() + name[1:] if name else name


# ---------------------------------------------------------------- schedule

def parse_event(event, season_type):
    comp = event['competitions'][0]
    competitors = comp['competitors']
    us = next((c for c in competitors if c['team']['id'] == WARRIORS_ESPN_ID), None)
    them = next((c for c in competitors if c['team']['id'] != WARRIORS_ESPN_ID), None)
    if not us or not them:
        return None

    tip = parse_utc(event['date'])
    local = tip.astimezone(PACIFIC_TZ)
    status = comp.get('status', {}).get('type', {})
    team = them['team']
    venue = comp.get('venue', {})
    address = venue.get('address', {})

    def score(c):
        s = c.get('score')
        if isinstance(s, dict):
            s = s.get('displayValue')
        try:
            return int(s)
        except (TypeError, ValueError):
            return None

    pts, opp_pts = score(us), score(them)
    final = status.get('completed') and pts is not None and opp_pts is not None
    wl = ('W' if pts > opp_pts else 'L') if final else None

    return {
        "id": event['id'],
        "tipUtc": to_utc_str(tip),
        "date": local.date().isoformat(),
        "time": local.strftime('%I:%M %p').lstrip('0') if event.get('timeValid', True) else 'TBD',
        "seasonType": season_type,
        "opponent": team.get('displayName'),
        "opponentShort": team.get('shortDisplayName'),
        "opponentAbbr": team.get('abbreviation'),
        "opponentId": team.get('id'),
        "opponentLogo": f"https://a.espncdn.com/i/teamlogos/nba/500-dark/{team.get('abbreviation', '').lower()}.png",
        "isHome": us.get('homeAway') == 'home',
        "neutral": bool(comp.get('neutralSite')),
        "arena": tidy_venue(venue.get('fullName')),
        "city": address.get('city'),
        "status": status.get('state', 'pre'),  # pre | in | post
        "wl": wl,
        "pts": pts if final else None,
        "oppPts": opp_pts if final else None,
        "tv": None,
    }


def get_schedule():
    print("Fetching schedule from ESPN...")
    games = []
    for season_type, label in ((1, 'pre'), (2, 'reg'), (3, 'post')):
        try:
            data = get_json(f"{ESPN_SITE}/teams/gs/schedule", params={'seasontype': season_type})
        except Exception as e:
            print(f"  {label} schedule failed: {e}")
            continue
        events = data.get('events', [])
        print(f"  {label}: {len(events)} games")
        for event in events:
            game = parse_event(event, label)
            if game:
                games.append(game)
    games.sort(key=lambda g: g['tipUtc'])
    return games


# ---------------------------------------------------------------- TV (Telus)

def channel_info(channel):
    call = channel.get('callSign', '')
    base = call[:-2] if call.endswith('HD') else call
    for suffix in ('HBO', 'BO', 'DT', 'CD', 'B'):
        if base.endswith(suffix) and base[:-len(suffix)] in CHANNEL_NAMES:
            base = base[:-len(suffix)]
            break
    name = CHANNEL_NAMES.get(base) or channel.get('affiliateName') or base
    thumb = channel.get('thumbnail') or ''
    if thumb.startswith('//'):
        thumb = 'https:' + thumb
    return {"name": name, "number": channel.get('channelNo'), "logo": thumb.split('?')[0] or None}


def find_tv(game):
    """Returns {'status': 'on'|'none'|'tba', ...} for one game."""
    tip = parse_utc(game['tipUtc'])
    params = dict(TELUS_LINEUP, timespan=3, isOverride='true', time=int((tip - timedelta(hours=1)).timestamp()),
                  pref='16,128', userId='-', aid='orbebb', languagecode='en-us')
    grid = get_json(GRACENOTE_GRID, params=params)
    channels = grid.get('channels') or []
    if not channels:
        return {"status": "tba"}

    # Is this slot actually listed yet? Near and past the horizon Gracenote
    # returns nothing or generic "To Be Announced" placeholders.
    window_end = tip + timedelta(hours=2, minutes=30)
    seen = 0
    for ch in channels:
        if ch.get('callSign') not in REFERENCE_CHANNELS:
            continue
        for ev in ch.get('events', []):
            if parse_utc(ev['startTime']) < window_end and parse_utc(ev['endTime']) > tip:
                seen += 1
                program = ev.get('program', {})
                if str(program.get('isGeneric') or '0') != '0' or program.get('title') == 'To Be Announced':
                    return {"status": "tba"}
    if not seen:
        return {"status": "tba"}

    candidates = []
    for ch in channels:
        try:
            number = int(ch.get('channelNo') or 0)
        except ValueError:
            continue
        # TELUS duplicates every channel in the 9000s as SD; NBA TV isn't
        # something we count as being on TV.
        if number >= 9000 or 'NBATV' in (ch.get('callSign') or ''):
            continue
        for ev in ch.get('events', []):
            p = ev.get('program', {})
            if 'Basketball' not in (p.get('title') or ''):
                continue
            if 'Golden State Warriors' not in (p.get('episodeTitle') or ''):
                continue
            start = parse_utc(ev['startTime'])
            offset = abs((start - tip).total_seconds())
            if offset > 90 * 60:
                continue
            live = 'Live' in (ev.get('flag') or [])
            candidates.append((not live, offset, number, ch))

    if not candidates:
        return {"status": "none"}
    candidates.sort(key=lambda c: c[:3])
    return dict(status="on", **channel_info(candidates[0][3]))


def add_tv(schedule, previous):
    print("Fetching TELUS TV listings...")
    prev_tv = {g['id']: g.get('tv') for g in previous if isinstance(g, dict) and g.get('id')}
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(days=16)
    for game in schedule:
        tip = parse_utc(game['tipUtc'])
        if game['status'] == 'post' or tip > horizon or tip < now - timedelta(hours=4):
            game['tv'] = prev_tv.get(game['id']) or ({"status": "tba"} if tip > now else None)
            continue
        try:
            game['tv'] = find_tv(game)
            print(f"  {game['date']} {game['opponentAbbr']}: {game['tv']}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  TV lookup failed for {game['date']} {game['opponentAbbr']}: {e}")
            game['tv'] = prev_tv.get(game['id']) or {"status": "tba"}


# ---------------------------------------------------------------- opponents

def fetch_standings(season_year):
    """{'west': [...], 'east': [...]} for one regular season, best seed first."""
    data = get_json(ESPN_STANDINGS, params={'season': season_year, 'seasontype': 2})
    conferences = {}
    for conf in data.get('children', []):
        key = (conf.get('abbreviation') or conf.get('name', '')).lower()
        key = 'east' if key.startswith('east') else 'west'
        rows = []
        for entry in conf.get('standings', {}).get('entries', []):
            stats = {s.get('name'): s for s in entry.get('stats', [])}
            team = entry['team']

            def num(name):
                try:
                    return float(stats[name].get('value'))
                except (KeyError, TypeError, ValueError):
                    return 0

            abbr = team.get('abbreviation', '')
            rows.append({
                "id": team.get('id'),
                "abbr": abbr,
                "name": team.get('shortDisplayName'),
                "logo": f"https://a.espncdn.com/i/teamlogos/nba/500-dark/{abbr.lower()}.png",
                "seed": int(num('playoffSeed')),
                "w": int(num('wins')),
                "l": int(num('losses')),
                "pct": (stats.get('winPercent') or {}).get('displayValue', '.000'),
                "gb": (stats.get('gamesBehind') or {}).get('displayValue', '-'),
                "record": (stats.get('overall') or {}).get('displayValue', '0-0'),
            })
        # Seeds are 0 before anyone has played; fall back to win % then name.
        rows.sort(key=lambda r: (r['seed'] or 99, -(r['w'] / max(r['w'] + r['l'], 1)), r['name'] or ''))
        conferences[key] = rows
    return conferences


def season_label(season_year):
    return f"{season_year - 1}\u2013{str(season_year)[2:]}"


def get_standings(season_year):
    """Current records for every team, plus the standings table to show.

    Until opening night the current season has no games, so the table shows
    last season's final standings instead.
    """
    records, standings = {}, None
    try:
        current = fetch_standings(season_year)
        for rows in current.values():
            for r in rows:
                records[r['id']] = r['record']
        started = any(r['w'] + r['l'] for rows in current.values() for r in rows)
        if started:
            standings = {"season": season_label(season_year), "final": False, "conferences": current}
        else:
            standings = {"season": season_label(season_year - 1), "final": True,
                         "conferences": fetch_standings(season_year - 1)}
    except Exception as e:
        print(f"  standings failed: {e}")
    return records, standings


def get_top_scorers(team_id, season_year):
    try:
        data = get_json(f"{ESPN_CORE}/seasons/{season_year}/types/2/teams/{team_id}/leaders")
    except Exception:
        return []  # no stats yet (before opening night)
    ppg = next((c for c in data.get('categories', []) if c.get('name') == 'pointsPerGame'), None)
    if not ppg:
        return []
    leaders = sorted(ppg.get('leaders', []), key=lambda l: l.get('value') or 0, reverse=True)[:3]
    scorers = []
    for leader in leaders:
        try:
            athlete = get_json(leader['athlete']['$ref'].replace('http://', 'https://'))
        except Exception:
            continue
        scorers.append({
            "name": athlete.get('displayName'),
            "position": (athlete.get('position') or {}).get('displayName'),
            "ppg": round(leader.get('value') or 0, 1),
            "img": (athlete.get('headshot') or {}).get('href'),
        })
    return scorers


def get_team_details(schedule, records, season_year):
    print("Fetching opponent top scorers...")
    details = {"_warriors": {"record": records.get(WARRIORS_ESPN_ID, '0-0')}}
    for team_id in sorted({g['opponentId'] for g in schedule if g.get('opponentId')}):
        details[team_id] = {
            "record": records.get(team_id, '0-0'),
            "scorers": get_top_scorers(team_id, season_year),
        }
        time.sleep(0.2)
    return details


# ---------------------------------------------------------------- news

def describe_injury(injury):
    d = injury.get('details') or {}
    part = (d.get('type') or 'Injury')
    if d.get('side') and d.get('side') not in ('Not Specified',):
        part = f"{d['side']} {part.lower()}"
    if d.get('detail'):
        part = f"{part} ({d['detail'].lower()})"
    return part


def get_news():
    print("Fetching injuries and news...")
    injuries = []
    try:
        data = get_json(f"{ESPN_SITE}/injuries")
        team = next((t for t in data.get('injuries', []) if t.get('id') == WARRIORS_ESPN_ID), {})
        for inj in team.get('injuries', []):
            athlete = inj.get('athlete', {})
            athlete_id = None
            for link in athlete.get('links', []):
                if '/id/' in link.get('href', ''):
                    athlete_id = link['href'].split('/id/')[1].split('/')[0]
                    break
            injuries.append({
                "athleteId": athlete_id,
                "name": athlete.get('displayName'),
                "position": (athlete.get('position') or {}).get('abbreviation'),
                "img": (athlete.get('headshot') or {}).get('href'),
                "status": inj.get('status'),
                "injury": describe_injury(inj),
                "returnDate": (inj.get('details') or {}).get('returnDate'),
                "comment": inj.get('shortComment'),
                "updated": inj.get('date'),
            })
    except Exception as e:
        print(f"  injuries failed: {e}")
        injuries = None

    articles = []
    try:
        data = get_json(f"{ESPN_SITE}/news", params={'team': WARRIORS_ESPN_ID, 'limit': 50})
        for a in data.get('articles', []):
            if a.get('type') == 'Media':  # highlight clips can spoil results
                continue
            teams = [c for c in a.get('categories', []) if c.get('type') == 'team']
            if not teams or any(str(c.get('teamId')) != WARRIORS_ESPN_ID for c in teams):
                continue
            url = (a.get('links', {}).get('web') or {}).get('href')
            if not url:
                continue
            articles.append({
                "headline": a.get('headline'),
                "published": a.get('published'),
                "url": url,
            })
    except Exception as e:
        print(f"  news failed: {e}")
        articles = None

    return injuries, articles[:12] if articles is not None else None


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    previous = load_json('schedule.json', [])

    schedule = get_schedule()
    if not schedule:
        raise RuntimeError("ESPN returned no games; keeping existing data.")
    add_tv(schedule, previous)
    write_json('schedule.json', schedule)
    print(f"Saved {len(schedule)} games to schedule.json")

    season_year = parse_utc(schedule[-1]['tipUtc']).year
    print("Fetching standings...")
    records, standings = get_standings(season_year)
    if standings:
        write_json('standings.json', standings)
        print("Saved standings.json")
    write_json('team_details.json', get_team_details(schedule, records, season_year))
    print("Saved team_details.json")

    injuries, articles = get_news()
    old_news = load_json('news.json', {})
    write_json('news.json', {
        "updated": to_utc_str(datetime.now(timezone.utc)),
        "curryId": CURRY_ESPN_ID,
        "injuries": injuries if injuries is not None else old_news.get('injuries', []),
        "articles": articles if articles is not None else old_news.get('articles', []),
    })
    print("Saved news.json")


if __name__ == "__main__":
    main()
