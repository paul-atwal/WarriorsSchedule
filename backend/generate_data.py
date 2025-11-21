import json
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder, leaguedashplayerstats, teaminfocommon
from nba_api.stats.static import teams
from datetime import datetime
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
        return games
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return []

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
            info = teaminfocommon.TeamInfoCommon(team_id=opp_id, season=SEASON)
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
    # details = get_team_details(schedule)
    # with open(f'{DATA_DIR}/team_details.json', 'w') as f:
    #     json.dump(details, f, indent=2)
    # print(f"Saved details for {len(details)} teams.")
    
    # NOTE: For speed in this demo, I'm skipping the heavy team_details fetch loop
    # and just creating a placeholder structure. You can uncomment above to run full fetch.
    placeholder_details = {}
    for g in schedule:
        opp_id = g['opponent_id']
        if opp_id not in placeholder_details:
            placeholder_details[opp_id] = {
                "record": "N/A",
                "scorers": []
            }
    with open(f'{DATA_DIR}/team_details.json', 'w') as f:
        json.dump(placeholder_details, f, indent=2)
    print("Saved placeholder team details.")

if __name__ == "__main__":
    main()
