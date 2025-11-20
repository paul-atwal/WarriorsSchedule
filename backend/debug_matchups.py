from nba_api.stats.endpoints import teamgamelog
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

try:
    print("Fetching Warriors Game Log for 2025-26...")
    gamelog = teamgamelog.TeamGameLog(team_id=1610612744, season='2025-26')
    df = gamelog.get_data_frames()[0]
    
    if df.empty:
        print("2025-26 log empty, trying 2024-25...")
        gamelog = teamgamelog.TeamGameLog(team_id=1610612744, season='2024-25')
        df = gamelog.get_data_frames()[0]

    print("\nColumns:", df.columns.tolist())
    
    # Print first few rows with relevant columns
    cols = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'Plus_Minus']
    # Check if 'PLUS_MINUS' exists instead
    if 'PLUS_MINUS' in df.columns:
        cols = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'PLUS_MINUS']
        
    print("\nFirst 5 rows:")
    print(df[cols].head())
    
    print("\nChecking data types:")
    print(df[cols].dtypes)

except Exception as e:
    print(f"Error: {e}")
