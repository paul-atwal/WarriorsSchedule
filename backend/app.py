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
CACHE_DURATION = timedelta(minutes=0)  # Temporarily disabled to force refresh

import json
import os

# Load static data
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_schedule():
    try:
        with open(os.path.join(DATA_DIR, 'schedule.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schedule: {e}")
        return []

def load_team_details():
    try:
        with open(os.path.join(DATA_DIR, 'team_details.json'), 'r') as f:
            return json.load(f)
    except:
        return {}

@app.route('/api/last-game')
def get_last_game():
    global cache
    now = datetime.now()
    
    # Check cache
    if cache["last_game"]["data"] and cache["last_game"]["timestamp"] and (now - cache["last_game"]["timestamp"] < CACHE_DURATION):
        print("Serving last-game from cache")
        return jsonify(cache["last_game"]["data"])

    try:
        schedule = load_schedule()
        now = datetime.now()
        today = now.date()
        
        # Find last played game
        last_game = None
        for game in reversed(schedule):
            game_date = datetime.strptime(game['date'], '%Y-%m-%d').date()
            
            # Game is definitely in the past
            if game_date < today:
                last_game = game
                break
            
            # Game is today - check if it's been at least 3 hours since start time
            if game_date == today and game.get('time'):
                try:
                    # Parse time like "07:00 PM PST"
                    time_str = game['time'].replace(' PST', '').replace(' PDT', '').strip()
                    game_time = datetime.strptime(time_str, '%I:%M %p')
                    # Combine date and time
                    game_datetime = datetime.combine(game_date, game_time.time())
                    # Check if at least 3 hours have passed
                    hours_since_start = (now - game_datetime).total_seconds() / 3600
                    if hours_since_start >= 3:
                        last_game = game
                        break
                except:
                    # If time parsing fails, skip this game (treat as future)
                    pass
        
        if not last_game:
            return jsonify(FALLBACK_LAST_GAME)

        # Generate YouTube highlights link
        query = f"Golden State Warriors vs {last_game['opponent']} {last_game['date']} highlights"
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        youtube_link = f"https://www.youtube.com/results?search_query={encoded_query}"

        data = {
            "id": last_game['id'],
            "date": last_game['date'],
            "matchup": f"GSW vs {last_game['opponent']}" if last_game['isHome'] else f"GSW @ {last_game['opponent']}",
            "opponent": last_game['opponent'],
            "wl": last_game['wl'],
            "pts": last_game['pts'],
            "plus_minus": last_game['plus_minus'],
            "youtubeLink": youtube_link
        }
        
        # Update cache
        cache["last_game"] = {"data": data, "timestamp": now}
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching last game: {e}. Returning fallback.")
        return jsonify(FALLBACK_LAST_GAME)

@app.route('/api/schedule')
def get_schedule():
    global cache
    now = datetime.now()
    
    # Check cache
    if cache["schedule"]["data"] and cache["schedule"]["timestamp"] and (now - cache["schedule"]["timestamp"] < CACHE_DURATION):
        print("Serving schedule from cache")
        return jsonify(cache["schedule"]["data"])

    try:
        schedule = load_schedule()
        today = datetime.now().date()
        
        future_games = []
        for game in schedule:
            # game['date'] is YYYY-MM-DD
            game_date = datetime.strptime(game['date'], '%Y-%m-%d').date()
            # If game is today or in future, include it
            if game_date >= today:
                future_games.append(game)
        
        # Limit to next 10
        future_games = future_games[:10]

        if future_games:
            cache["schedule"] = {"data": future_games, "timestamp": now}
            return jsonify(future_games)
        else:
            return jsonify(FALLBACK_SCHEDULE)
            
    except Exception as e:
        print(f"Error fetching schedule: {e}. Returning fallback.")
        return jsonify(FALLBACK_SCHEDULE)

@app.route('/api/game/<game_id>')
def get_game_details(game_id):
    print(f"API Request: get_game_details for {game_id}")
    
    global cache
    now = datetime.now()
    game_id = str(game_id) # JSON IDs are ints, but we might receive string
    
    # Check cache
    if game_id in cache["game_details"]:
        entry = cache["game_details"][game_id]
        if entry["timestamp"] and (now - entry["timestamp"] < CACHE_DURATION):
            print(f"Serving game {game_id} from cache")
            return jsonify(entry["data"])

    try:
        schedule = load_schedule()
        team_details = load_team_details()
        
        # Find game in schedule
        target_game = None
        for g in schedule:
            if str(g['id']) == game_id:
                target_game = g
                break
        
        if not target_game:
            return jsonify({"error": "Game not found"}), 404

        opp_id = str(target_game['opponent_id'])
        details = team_details.get(opp_id, {"record": "N/A", "scorers": []})
        
        # Calculate Head-to-Head from schedule
        h2h_list = []
        for g in schedule:
            if str(g['opponent_id']) == opp_id and g['wl']: # Played game against same opponent
                 h2h_list.append({
                    "date": g['date'],
                    "score": g['score'],
                    "result": g['wl']
                })
        
        # Reverse to show most recent first
        h2h_list.reverse()

        response_data = {
            "opponent": target_game['opponent'],
            "record": details['record'],
            "scorers": details['scorers'],
            "h2h": h2h_list
        }
        
        # Update cache
        cache["game_details"][game_id] = {"data": response_data, "timestamp": now}
        
        return jsonify(response_data)
    except Exception as e:
        print(f"Error fetching game details: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
