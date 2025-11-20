from flask import Flask, jsonify
from flask_cors import CORS
from nba_api.stats.endpoints import scoreboardv2, leaguegamefinder
from nba_api.stats.static import teams
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)
CORS(app)

# Warriors Team ID
WARRIORS_ID = 1610612744

# Simple in-memory cache
cache = {
    "schedule": {"data": [], "timestamp": None},
    "last_game": {"data": None, "timestamp": None},
    "game_details": {} # Key: game_id, Value: {data, timestamp}
}
CACHE_DURATION = timedelta(minutes=30)

@app.route('/api/last-game')
def get_last_game():
    global cache
    now = datetime.now()
    
    # Check cache
    if cache["last_game"]["data"] and cache["last_game"]["timestamp"] and (now - cache["last_game"]["timestamp"] < CACHE_DURATION):
        print("Serving last-game from cache")
        return jsonify(cache["last_game"]["data"])

    try:
        # Get Warriors game log via LeagueGameFinder (has PLUS_MINUS)
        finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=WARRIORS_ID, season_nullable='2025-26')
        df = finder.get_data_frames()[0]
        
        if df.empty:
             # Fallback to 2024-25
            finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=WARRIORS_ID, season_nullable='2024-25')
            df = finder.get_data_frames()[0]
            
        last_game = df.iloc[0]
        
        # Handle PLUS_MINUS safely
        plus_minus = last_game.get('PLUS_MINUS', 0)
        if pd.isna(plus_minus): plus_minus = 0
        
        # Parse opponent name from MATCHUP
        matchup = last_game['MATCHUP']
        opponent_abbrev = matchup.split(' ')[-1] # Get last part (POR)
        opponent_info = teams.find_team_by_abbreviation(opponent_abbrev)
        opponent_full_name = opponent_info['full_name'] if opponent_info else opponent_abbrev

        # Generate YouTube highlights link
        # Query: "Golden State Warriors vs {Opponent} {Date} highlights"
        query = f"Golden State Warriors vs {opponent_full_name} {last_game['GAME_DATE']} highlights"
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        youtube_link = f"https://www.youtube.com/results?search_query={encoded_query}"

        data = {
            "id": int(last_game['GAME_ID']),
            "date": last_game['GAME_DATE'],
            "matchup": matchup,
            "opponent": opponent_full_name, # Add full name for logo
            "wl": last_game['WL'],
            "pts": int(last_game['PTS']),
            "plus_minus": int(plus_minus),
            "youtubeLink": youtube_link
        }
        
        # Update cache
        cache["last_game"] = {"data": data, "timestamp": now}
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching last game: {e}")
        return jsonify({"error": str(e)}), 500

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
    except:
        return time_str

@app.route('/api/schedule')
def get_schedule():
    global cache
    now = datetime.now()
    
    # Check cache
    if cache["schedule"]["data"] and cache["schedule"]["timestamp"] and (now - cache["schedule"]["timestamp"] < CACHE_DURATION):
        print("Serving schedule from cache")
        return jsonify(cache["schedule"]["data"])

    try:
        # Get scoreboard for a range of dates
        # Fetch next 7 days (reduced from 14) using parallel threads to prevent timeout
        today = datetime.now()
        games = []
        dates = [(today + timedelta(days=i)).strftime('%m/%d/%Y') for i in range(7)]
        
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def fetch_games_for_date(date_str):
            found_games = []
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
                        
                        found_games.append({
                            "id": game['GAME_ID'],
                            "date": game['GAME_DATE_EST'],
                            "time": convert_to_pst(game['GAME_STATUS_TEXT']),
                            "opponent": opponent_name,
                            "isHome": is_home,
                            "location": "Chase Center" if is_home else "Away"
                        })
            except Exception as e:
                print(f"Error fetching schedule for {date_str}: {e}")
            return found_games

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_date = {executor.submit(fetch_games_for_date, d): d for d in dates}
            for future in as_completed(future_to_date):
                games.extend(future.result())
        
        # Sort games by date
        games.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%dT%H:%M:%S') if 'T' in x['date'] else datetime.strptime(x['date'], '%Y-%m-%d') if '-' in x['date'] else datetime.now()) # Fallback sort

        if games:
            cache["schedule"] = {"data": games, "timestamp": now}
        
        return jsonify(games)
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return jsonify([]), 500

@app.route('/api/game/<game_id>')
def get_game_details(game_id):
    print(f"API Request: get_game_details for {game_id}")
    
    global cache
    now = datetime.now()
    game_id = str(game_id).zfill(10)
    
    # Check cache
    if game_id in cache["game_details"]:
        entry = cache["game_details"][game_id]
        if entry["timestamp"] and (now - entry["timestamp"] < CACHE_DURATION):
            print(f"Serving game {game_id} from cache")
            return jsonify(entry["data"])

    try:
        print(f"Padded Game ID: {game_id}")

        # 1. Try BoxScoreSummaryV2 first
        from nba_api.stats.endpoints import boxscoresummaryv2
        try:
            summary = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id, timeout=10).game_summary.get_data_frame()
        except Exception as e:
            print(f"BoxScoreSummaryV2 error: {e}")
            summary = pd.DataFrame()
        
        opponent_id = None
        opponent_name = "Unknown"
        
        if not summary.empty:
            print("BoxScoreSummaryV2 found data.")
            game_data = summary.iloc[0]
            home_id = game_data['HOME_TEAM_ID']
            visitor_id = game_data['VISITOR_TEAM_ID']
            opponent_id = visitor_id if home_id == WARRIORS_ID else home_id
        else:
            # Fallback: Search upcoming schedule
            print(f"BoxScoreSummaryV2 failed/empty for {game_id}, searching schedule...")
            today = datetime.now()
            for i in range(30): # Look ahead 30 days
                date_str = (today + timedelta(days=i)).strftime('%m/%d/%Y')
                try:
                    board = scoreboardv2.ScoreboardV2(game_date=date_str, timeout=5)
                    header = board.game_header.get_data_frame()
                    if not header.empty:
                        match = header[header['GAME_ID'] == game_id]
                        if not match.empty:
                            print(f"Found game in schedule on {date_str}")
                            game_data = match.iloc[0]
                            is_home = game_data['HOME_TEAM_ID'] == WARRIORS_ID
                            opponent_id = game_data['VISITOR_TEAM_ID'] if is_home else game_data['HOME_TEAM_ID']
                            break
                except Exception as e:
                    print(f"Error searching schedule date {date_str}: {e}")
        
        if not opponent_id:
             print("Opponent ID could not be determined.")
             return jsonify({"error": "Game not found"}), 404

        opponent_info = teams.find_team_name_by_id(opponent_id)
        opponent_name = opponent_info['full_name']
        print(f"Opponent: {opponent_name} (ID: {opponent_id})")
        
        # 2. Get Opponent Record (from TeamInfoCommon or Standings)
        from nba_api.stats.endpoints import teaminfocommon
        try:
            team_info = teaminfocommon.TeamInfoCommon(team_id=opponent_id, timeout=10).team_info_common.get_data_frame()
            record = f"{team_info.iloc[0]['W']}-{team_info.iloc[0]['L']}"
        except Exception as e:
            print(f"Error fetching record: {e}")
            record = "N/A"
        
        # 3. Get Top Scorers (from PlayerStats)
        from nba_api.stats.endpoints import leaguedashplayerstats
        try:
            player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                team_id_nullable=opponent_id, 
                season='2025-26',
                timeout=10
            ).league_dash_player_stats.get_data_frame()
            
            if player_stats.empty:
                 player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                    team_id_nullable=opponent_id, 
                    season='2024-25',
                    timeout=10
                ).league_dash_player_stats.get_data_frame()

            top_scorers = player_stats.sort_values('PTS', ascending=False).head(3)
            scorers_list = []
            for _, player in top_scorers.iterrows():
                scorers_list.append({
                    "name": player['PLAYER_NAME'],
                    "ppg": round(player['PTS'] / player['GP'], 1),
                    "img": f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player['PLAYER_ID']}.png"
                })
        except Exception as e:
            print(f"Error fetching scorers: {e}")
            scorers_list = []
            
        # 4. Season Matchups (LeagueGameFinder filtered by opponent)
        try:
            finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=WARRIORS_ID, season_nullable='2025-26', timeout=10)
            gamelog = finder.get_data_frames()[0]
            opp_abbrev = opponent_info['abbreviation']
            h2h_games = gamelog[gamelog['MATCHUP'].str.contains(opp_abbrev)]
            h2h_list = []
            for _, h_game in h2h_games.iterrows():
                # Safe PLUS_MINUS access
                pm = h_game.get('PLUS_MINUS', 0)
                if pd.isna(pm): pm = 0
                
                h2h_list.append({
                    "date": h_game['GAME_DATE'],
                    "score": f"{h_game['WL']} {h_game['PTS']}-{int(h_game['PTS']) - int(pm)}",
                    "result": h_game['WL']
                })
        except Exception as e:
            print(f"Error fetching matchups: {e}")
            h2h_list = []

        response_data = {
            "opponent": opponent_name,
            "record": record,
            "scorers": scorers_list,
            "h2h": h2h_list
        }
        
        # Update cache
        cache["game_details"][game_id] = {"data": response_data, "timestamp": now}
        
        print("Successfully constructed response.")
        return jsonify(response_data)
    except Exception as e:
        print(f"Error fetching game details: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
