import json
import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
from nba_api.stats.endpoints import leaguegamefinder, leaguedashplayerstats, teaminfocommon
from nba_api.stats.static import teams

# Configuration
WARRIORS_ID = 1610612744
DEFAULT_SEASON = '2025-26'
DATA_DIR = 'backend/data'
SCHEDULE_URL = 'https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json'

try:
    from zoneinfo import ZoneInfo
    PACIFIC_TZ = ZoneInfo("America/Los_Angeles")
    EASTERN_TZ = ZoneInfo("America/New_York")
except Exception:
    PACIFIC_TZ = timezone(timedelta(hours=-8))
    EASTERN_TZ = timezone(timedelta(hours=-5))

def load_existing_schedule():
    path = os.path.join(DATA_DIR, 'schedule.json')
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading existing schedule: {e}")
    return []

def format_team_name(team):
    city = (team.get('teamCity') or '').strip()
    name = (team.get('teamName') or '').strip()
    if city and name:
        return f"{city} {name}"
    return name or team.get('teamTricode') or "Unknown"

def parse_game_datetime(game):
    utc_str = game.get('gameDateTimeUTC')
    if utc_str:
        try:
            dt_utc = datetime.fromisoformat(utc_str.replace('Z', '+00:00'))
            return dt_utc.astimezone(PACIFIC_TZ)
        except Exception:
            pass
    date_est = game.get('gameDateEst')
    time_est = game.get('gameTimeEst')
    if date_est and time_est and any(ch.isdigit() for ch in time_est):
        try:
            dt_est = datetime.strptime(f"{date_est} {time_est}", "%m/%d/%Y %I:%M %p").replace(tzinfo=EASTERN_TZ)
            return dt_est.astimezone(PACIFIC_TZ)
        except Exception:
            pass
    return None

def format_time_pacific(dt_local):
    if not dt_local:
        return "TBD"
    time_str = dt_local.strftime("%I:%M %p %Z").lstrip("0")
    if time_str.endswith("UTC-08:00"):
        time_str = time_str.replace("UTC-08:00", "PST")
    return time_str

def parse_game_date(game, dt_local):
    if dt_local:
        return dt_local.date().isoformat()
    date_est = game.get('gameDateEst')
    if date_est:
        try:
            return datetime.strptime(date_est, "%m/%d/%Y").date().isoformat()
        except Exception:
            pass
    date_utc = game.get('gameDateUTC')
    if date_utc:
        try:
            return datetime.strptime(date_utc, "%Y-%m-%d").date().isoformat()
        except Exception:
            pass
    return None

def parse_result(home, away, is_home, game_status):
    if game_status != 3:
        return None, None, 0, 0
    try:
        home_score = int(home.get('score', 0))
        away_score = int(away.get('score', 0))
    except Exception:
        return None, None, 0, 0
    pts = home_score if is_home else away_score
    opp_pts = away_score if is_home else home_score
    wl = "W" if pts > opp_pts else "L"
    score = f"{wl} {pts}-{opp_pts}"
    return wl, score, pts, pts - opp_pts

def get_schedule_from_cdn():
    print("Fetching Schedule from CDN...")
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WarriorsSchedule/1.0)",
        "Accept": "application/json",
    }
    response = requests.get(SCHEDULE_URL, headers=headers, timeout=20)
    response.raise_for_status()
    payload = response.json()
    league = payload.get('leagueSchedule', {})
    season_year = league.get('seasonYear') or DEFAULT_SEASON

    games = []
    for date_block in league.get('gameDates', []):
        for game in date_block.get('games', []):
            if game.get('gameLabel') == 'Preseason':
                continue
            home = game.get('homeTeam', {})
            away = game.get('awayTeam', {})
            try:
                home_id = int(home.get('teamId', 0) or 0)
                away_id = int(away.get('teamId', 0) or 0)
            except Exception:
                continue
            if WARRIORS_ID not in (home_id, away_id):
                continue

            is_home = home_id == WARRIORS_ID
            opponent = away if is_home else home
            opponent_id = int(opponent.get('teamId', 0) or 0)
            opponent_name = format_team_name(opponent)

            dt_local = parse_game_datetime(game)
            date_str = parse_game_date(game, dt_local)
            if not date_str:
                continue
            time_str = format_time_pacific(dt_local)

            wl, score, pts, plus_minus = parse_result(home, away, is_home, game.get('gameStatus'))
            games.append({
                "id": game.get('gameId'),
                "date": date_str,
                "time": time_str,
                "opponent": opponent_name,
                "opponent_id": opponent_id,
                "isHome": is_home,
                "location": game.get('arenaName') or ("Chase Center" if is_home else "Away"),
                "score": score,
                "wl": wl,
                "pts": int(pts),
                "plus_minus": int(plus_minus)
            })

    games.sort(key=lambda x: x['date'])
    return games, season_year

def get_schedule_from_nba_api(season):
    print("Fetching Schedule via nba_api fallback...")
    try:
        finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=WARRIORS_ID, season_nullable=season)
        df = finder.get_data_frames()[0]

        games = []
        for _, game in df.iterrows():
            game_date_str = game['GAME_DATE']
            matchup = game['MATCHUP']
            is_home = 'vs.' in matchup
            opponent_abbrev = matchup.split(' ')[-1]

            opp_info = teams.find_team_by_abbreviation(opponent_abbrev)
            opponent_name = opp_info['full_name'] if opp_info else opponent_abbrev
            opponent_id = opp_info['id'] if opp_info else 0

            wl = game['WL']
            pts = game['PTS']
            plus_minus = game['PLUS_MINUS'] if pd.notna(game['PLUS_MINUS']) else 0

            score = None
            if wl:
                opp_pts = int(pts - plus_minus)
                score = f"{wl} {int(pts)}-{opp_pts}"

            games.append({
                "id": str(game['GAME_ID']),
                "date": game_date_str,
                "time": "TBD",
                "opponent": opponent_name,
                "opponent_id": int(opponent_id),
                "isHome": is_home,
                "location": "Chase Center" if is_home else "Away",
                "score": score,
                "wl": wl,
                "pts": int(pts) if pd.notna(pts) else 0,
                "plus_minus": int(plus_minus)
            })

        games.sort(key=lambda x: x['date'])
        return games
    except Exception as e:
        print(f"Error fetching schedule via nba_api: {e}")
        return []

def get_schedule():
    try:
        return get_schedule_from_cdn()
    except Exception as e:
        print(f"CDN schedule fetch failed: {e}")
        fallback_games = get_schedule_from_nba_api(DEFAULT_SEASON)
        return fallback_games, DEFAULT_SEASON

def get_team_details(schedule, season):
    print("Fetching Team Details (Records & Scorers)...")
    team_details = {}
    
    # Get unique opponents
    opponent_ids = set(g['opponent_id'] for g in schedule if g['opponent_id'] != 0)
    
    for opp_id in opponent_ids:
        try:
            print(f"Processing team {opp_id}...")
            # 1. Get Record
            # We can get this from TeamInfoCommon
            time.sleep(0.600) # Rate limit
            info = teaminfocommon.TeamInfoCommon(team_id=opp_id, season_nullable=season)
            info_df = info.team_info_common.get_data_frame()
            record = "0-0"
            if not info_df.empty:
                w = info_df.iloc[0]['W']
                l = info_df.iloc[0]['L']
                record = f"{w}-{l}"
            
            # 2. Get Top Scorers
            time.sleep(0.600)
            stats = leaguedashplayerstats.LeagueDashPlayerStats(team_id_nullable=opp_id, season=season)
            stats_df = stats.league_dash_player_stats.get_data_frame()
            
            scorers = []
            if not stats_df.empty:
                top3 = stats_df.sort_values('PTS', ascending=False).head(3)
                for _, p in top3.iterrows():
                    scorers.append({
                        "name": p['PLAYER_NAME'],
                        "ppg": round(p['PTS'] / p['GP'], 1),
                        "img": f"https://cdn.nba.com/headshots/nba/latest/1040x760/{p['PLAYER_ID']}.png"
                    })
            
            team_details[opp_id] = {
                "record": record,
                "scorers": scorers
            }
            
        except Exception as e:
            print(f"Error fetching details for {opp_id}: {e}")
            continue
            
    return team_details

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    # 1. Generate Schedule
    schedule, season_year = get_schedule()
    if not schedule:
        print("Schedule fetch returned no games. Falling back to existing data if available.")
        existing = load_existing_schedule()
        if existing:
            schedule = existing
        else:
            raise RuntimeError("No schedule data available to write.")
    with open(f'{DATA_DIR}/schedule.json', 'w') as f:
        json.dump(schedule, f, indent=2)
    print(f"Saved {len(schedule)} games to schedule.json")
    
    # 2. Generate Team Details
    details = get_team_details(schedule, season_year)
    with open(f'{DATA_DIR}/team_details.json', 'w') as f:
        json.dump(details, f, indent=2)
    print(f"Saved details for {len(details)} teams.")
    
    # NOTE: Real data fetching enabled.
    # placeholder_details = {}
    # for g in schedule:
    #     opp_id = g['opponent_id']
    #     if opp_id not in placeholder_details:
    #         placeholder_details[opp_id] = {
    #             "record": "N/A",
    #             "scorers": []
    #         }
    # with open(f'{DATA_DIR}/team_details.json', 'w') as f:
    #     json.dump(placeholder_details, f, indent=2)
    # print("Saved placeholder team details.")

if __name__ == "__main__":
    main()
