from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd

game_id = '0022500256' 
print(f"Testing Game ID: {game_id}")

try:
    finder = leaguegamefinder.LeagueGameFinder(game_id_nullable=game_id)
    games = finder.get_data_frames()[0]
    print("Games found:")
    print(games)
    
    if not games.empty:
        # Check if we can get opponent info
        # LeagueGameFinder returns one row per team in the game usually
        print(games[['TEAM_ID', 'TEAM_NAME', 'MATCHUP', 'GAME_DATE']])
except Exception as e:
    print(f"Error: {e}")
