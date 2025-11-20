from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.static import teams
from datetime import datetime, timedelta
import pandas as pd

WARRIORS_ID = 1610612744

def convert_to_pst(time_str):
    try:
        # Expected format: "7:30 pm ET"
        if time_str and "ET" in time_str:
            time_str = time_str.replace(" ET", "")
            dt = datetime.strptime(time_str, "%I:%M %p")
            # Subtract 3 hours
            dt_pst = dt - timedelta(hours=3)
            return f"{dt_pst.strftime('%I:%M %p')} PST"
        return time_str
    except Exception as e:
        print(f"Error converting time '{time_str}': {e}")
        return time_str

def get_schedule():
    try:
        today = datetime.now()
        games = []
        
        print("Fetching schedule...")
        for i in range(14):
            date_str = (today + timedelta(days=i)).strftime('%m/%d/%Y')
            print(f"Checking {date_str}...")
            board = scoreboardv2.ScoreboardV2(game_date=date_str)
            header = board.game_header.get_data_frame()
            
            if not header.empty:
                warriors_games = header[
                    (header['HOME_TEAM_ID'] == WARRIORS_ID) | 
                    (header['VISITOR_TEAM_ID'] == WARRIORS_ID)
                ]
                
                for _, game in warriors_games.iterrows():
                    print(f"Found game: {game['GAME_ID']}")
                    is_home = game['HOME_TEAM_ID'] == WARRIORS_ID
                    opponent_id = game['VISITOR_TEAM_ID'] if is_home else game['HOME_TEAM_ID']
                    
                    opp_info = teams.find_team_name_by_id(opponent_id)
                    opponent_name = opp_info['full_name'] if opp_info else "Unknown"
                    
                    game_time = game['GAME_STATUS_TEXT']
                    print(f"Time: {game_time}")
                    
                    games.append({
                        "id": game['GAME_ID'],
                        "date": game['GAME_DATE_EST'],
                        "time": convert_to_pst(game_time),
                        "opponent": opponent_name,
                        "isHome": is_home,
                        "location": "Chase Center" if is_home else "Away"
                    })
        
        print(f"Found {len(games)} games.")
        return games
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_schedule()
