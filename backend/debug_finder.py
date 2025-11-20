from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

try:
    print("Fetching Warriors Games via LeagueGameFinder...")
    finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=1610612744, season_nullable='2025-26')
    df = finder.get_data_frames()[0]
    
    print("\nColumns:", df.columns.tolist())
    
    if 'PLUS_MINUS' in df.columns:
        print("\nPLUS_MINUS found!")
        print(df[['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'PLUS_MINUS']].head())
    else:
        print("\nPLUS_MINUS NOT found.")

except Exception as e:
    print(f"Error: {e}")
