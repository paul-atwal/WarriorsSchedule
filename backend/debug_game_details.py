from nba_api.stats.endpoints import boxscoresummaryv2, teaminfocommon, leaguedashplayerstats, teamgamelog
from nba_api.stats.static import teams
from datetime import datetime, timedelta
import pandas as pd

WARRIORS_ID = 1610612744

def get_game_details_debug(game_id):
    print(f"Debugging Game ID: {game_id}")
    try:
        game_id = str(game_id).zfill(10)
        
        # 1. Try BoxScoreSummaryV2
        print("1. Fetching BoxScoreSummaryV2...")
        summary = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id).game_summary.get_data_frame()
        
        opponent_id = None
        opponent_name = "Unknown"
        
        if not summary.empty:
            print("Summary found.")
            game_data = summary.iloc[0]
            home_id = game_data['HOME_TEAM_ID']
            visitor_id = game_data['VISITOR_TEAM_ID']
            opponent_id = visitor_id if home_id == WARRIORS_ID else home_id
        else:
            print("Summary empty. Searching schedule...")
            # Fallback: Search upcoming schedule
            from nba_api.stats.endpoints import scoreboardv2
            today = datetime.now()
            for i in range(30): # Look ahead 30 days
                date_str = (today + timedelta(days=i)).strftime('%m/%d/%Y')
                board = scoreboardv2.ScoreboardV2(game_date=date_str)
                header = board.game_header.get_data_frame()
                if not header.empty:
                    match = header[header['GAME_ID'] == game_id]
                    if not match.empty:
                        print(f"Found in schedule on {date_str}")
                        game_data = match.iloc[0]
                        is_home = game_data['HOME_TEAM_ID'] == WARRIORS_ID
                        opponent_id = game_data['VISITOR_TEAM_ID'] if is_home else game_data['HOME_TEAM_ID']
                        break
        
        if not opponent_id:
             print("Opponent ID not found.")
             return

        print(f"Opponent ID: {opponent_id}")
        opponent_info = teams.find_team_name_by_id(opponent_id)
        opponent_name = opponent_info['full_name']
        print(f"Opponent Name: {opponent_name}")
        
        # 2. Get Opponent Record
        print("2. Fetching TeamInfoCommon...")
        team_info = teaminfocommon.TeamInfoCommon(team_id=opponent_id).team_info_common.get_data_frame()
        if not team_info.empty:
            record = f"{team_info.iloc[0]['W']}-{team_info.iloc[0]['L']}"
            print(f"Record: {record}")
        else:
            print("Team info empty.")
        
        # 3. Get Top Scorers
        print("3. Fetching LeagueDashPlayerStats...")
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            team_id_nullable=opponent_id, 
            season='2024-25'
        ).league_dash_player_stats.get_data_frame()
        
        if player_stats.empty:
             print("2024-25 stats empty. Trying 2023-24...")
             player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                team_id_nullable=opponent_id, 
                season='2023-24'
            ).league_dash_player_stats.get_data_frame()

        if not player_stats.empty:
            top_scorers = player_stats.sort_values('PTS', ascending=False).head(3)
            print(f"Top Scorers: {top_scorers['PLAYER_NAME'].tolist()}")
        else:
            print("Player stats empty.")
            
        # 4. Season Matchups
        print("4. Fetching TeamGameLog...")
        gamelog = teamgamelog.TeamGameLog(team_id=WARRIORS_ID, season='2024-25').team_game_log.get_data_frame()
        opp_abbrev = opponent_info['abbreviation']
        print(f"Filtering for {opp_abbrev}...")
        h2h_games = gamelog[gamelog['MATCHUP'].str.contains(opp_abbrev)]
        print(f"Found {len(h2h_games)} matchups.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Use the ID from the screenshot/previous logs: 0022500056 (Portland)
    get_game_details_debug("0022500056")
