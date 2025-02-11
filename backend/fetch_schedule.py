import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json 

# constants 
YEAR = 2024
WARRIORS_TEAM_ID = 1610612744
url = f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{YEAR}/league/00_full_schedule.json"

import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Constants
YEAR = 2024
WARRIORS_TEAM_ID = 1610612744
URL = f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{YEAR}/league/00_full_schedule.json"

def fetch_warriors_schedule():
    """Fetch all Warriors games from the NBA API."""
    r = requests.get(URL)

    if r.status_code != 200:
        print("Error fetching schedule:", r.status_code)
        return []

    data = r.json()

    current_month = datetime.now().strftime('%B')
    next_month = (datetime.now() + relativedelta(months=1)).strftime('%B')

    warriors_games = []

    for month in data["lscd"]:
        month_name = month["mscd"]["mon"]

        if month_name in [current_month, next_month]:
            for game in month["mscd"]["g"]:
                home_team = game["h"]
                away_team = game["v"]

                if home_team["tid"] == WARRIORS_TEAM_ID or away_team["tid"] == WARRIORS_TEAM_ID:
                    warriors_games.append(game)

    return warriors_games 