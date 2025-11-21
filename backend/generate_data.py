import json
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder, leaguedashplayerstats, teaminfocommon
from nba_api.stats.static import teams
from datetime import datetime, timedelta
import time
import os

# Configuration
WARRIORS_ID = 1610612744
SEASON = '2025-26'
DATA_DIR = 'backend/data'

def get_schedule():
    print("Fetching Schedule...")
    try:
        # Get all games for the season
        finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=WARRIORS_ID, season_nullable=SEASON)
        df = finder.get_data_frames()[0]
        
        games = []
        for _, game in df.iterrows():
            game_date_str = game['GAME_DATE'] # YYYY-MM-DD
            matchup = game['MATCHUP']
            is_home = 'vs.' in matchup
            opponent_abbrev = matchup.split(' ')[-1]
            
            # Get Opponent Full Name
            opp_info = teams.find_team_by_abbreviation(opponent_abbrev)
            opponent_name = opp_info['full_name'] if opp_info else opponent_abbrev
            opponent_id = opp_info['id'] if opp_info else 0
            
            # Determine Result/Score if played
            wl = game['WL']
            pts = game['PTS']
            plus_minus = game['PLUS_MINUS'] if pd.notna(game['PLUS_MINUS']) else 0
            
            score = None
            if wl:
                opp_pts = int(pts - plus_minus)
                score = f"{wl} {int(pts)}-{opp_pts}"

            games.append({
                "id": int(game['GAME_ID']),
                "date": game_date_str,
                "time": "TBD", # LeagueGameFinder lacks time, we can manually fix or accept TBD for now
                "opponent": opponent_name,
                "opponent_id": int(opponent_id),
                "isHome": is_home,
                "location": "Chase Center" if is_home else "Away",
                "score": score,
                "wl": wl,
                "pts": int(pts) if pd.notna(pts) else 0,
                "plus_minus": int(plus_minus)
            })
        
        # Sort by date
        games.sort(key=lambda x: x['date'])
        
        # Check if we have future games
        last_game_date = datetime.strptime(games[-1]['date'], '%Y-%m-%d').date() if games else datetime.now().date()
        today = datetime.now().date()
        
        if last_game_date < today + timedelta(days=30):
            print("Fetching future schedule via ScoreboardV2...")
            from nba_api.stats.endpoints import scoreboardv2
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            # Fetch next 60 days
            future_dates = [(today + timedelta(days=i)).strftime('%m/%d/%Y') for i in range(60)]
            
            def fetch_future_games(date_str):
                found = []
                try:
                    board = scoreboardv2.ScoreboardV2(game_date=date_str, timeout=5)
                    header = board.game_header.get_data_frame()
                    if not header.empty:
                        warriors_games = header[
                            (header['HOME_TEAM_ID'] == WARRIORS_ID) | 
                            (header['VISITOR_TEAM_ID'] == WARRIORS_ID)
                        ]
                        for _, game in warriors_games.iterrows():
                            is_home = game['HOME_TEAM_ID'] == WARRIORS_ID
                            opponent_id = game['VISITOR_TEAM_ID'] if is_home else game['HOME_TEAM_ID']
                            opp_info = teams.find_team_name_by_id(opponent_id)
                            opponent_name = opp_info['full_name'] if opp_info else "Unknown"
                            
                            # Avoid duplicates if LeagueGameFinder already found it
                            game_id = int(game['GAME_ID'])
                            
                            found.append({
                                "id": game_id,
                                "date": datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d'),
                                "time": convert_to_pst(game['GAME_STATUS_TEXT']),
                                "opponent": opponent_name,
                                "opponent_id": int(opponent_id),
                                "isHome": is_home,
                                "location": "Chase Center" if is_home else "Away",
                                "score": None,
                                "wl": None,
                                "pts": 0,
                                "plus_minus": 0
                            })
                except:
                    pass
                return found

            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_date = {executor.submit(fetch_future_games, d): d for d in future_dates}
                for future in as_completed(future_to_date):
                    new_games = future.result()
                    for ng in new_games:
                        # Check for duplicates by ID
                        if not any(g['id'] == ng['id'] for g in games):
                            games.append(ng)
            
            # Re-sort
            games.sort(key=lambda x: x['date'])

        return games
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return []

def convert_to_pst(time_str):
    from datetime import timedelta
    try:
        if time_str and "ET" in time_str:
            time_str = time_str.replace(" ET", "")
            dt = datetime.strptime(time_str, "%I:%M %p")
            dt_pst = dt - timedelta(hours=3)
            return f"{dt_pst.strftime('%I:%M %p')} PST"
        return time_str
    except:
        return time_str

def get_team_details(schedule):
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
            info = teaminfocommon.TeamInfoCommon(team_id=opp_id, season_nullable=SEASON)
            info_df = info.team_info_common.get_data_frame()
            record = "0-0"
            if not info_df.empty:
                w = info_df.iloc[0]['W']
                l = info_df.iloc[0]['L']
                record = f"{w}-{l}"
            
            # 2. Get Top Scorers
            time.sleep(0.600)
            stats = leaguedashplayerstats.LeagueDashPlayerStats(team_id_nullable=opp_id, season=SEASON)
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
    schedule = get_schedule()
    with open(f'{DATA_DIR}/schedule.json', 'w') as f:
        json.dump(schedule, f, indent=2)
    print(f"Saved {len(schedule)} games to schedule.json")
    
    # 2. Generate Team Details
    details = get_team_details(schedule)
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
