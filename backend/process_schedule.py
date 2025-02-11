from datetime import datetime, timedelta
import pytz
from fetch_schedule import fetch_warriors_schedule

# Define timezones
ET_TZ = pytz.timezone("America/New_York")  # Eastern Time
PST_TZ = pytz.timezone("America/Los_Angeles")  # Pacific Time

def filter_upcoming_games(games):
    """Filter games to only include the next 7 days and format them in PST."""
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    formatted_games = []

    for game in games:
        game_date = datetime.strptime(game["gdte"], "%Y-%m-%d").date()

        if today <= game_date <= next_week:
            # Convert game time from ET to PST
            game_datetime = datetime.strptime(game["etm"], "%Y-%m-%dT%H:%M:%S")
            game_datetime = ET_TZ.localize(game_datetime).astimezone(PST_TZ)
            game_time_pst = game_datetime.strftime("%I:%M %p")  # Convert to readable format

            # Determine opponent (city + team name)
            home_team = game["h"]
            away_team = game["v"]

            if home_team["tid"] == 1610612744:
                opponent = f"vs {away_team['tc']} {away_team['tn']}"
            else:
                opponent = f"@ {home_team['tc']} {home_team['tn']}"

            formatted_games.append({"date": game_date.strftime("%b %d"), "time": game_time_pst, "opponent": opponent})

    return formatted_games

def format_schedule_message(upcoming_games):
    message = "Warriors Games (Next 7 Days) - PST:\n"
    for game in upcoming_games:
        message += f"- {game['date']}: {game['opponent']} at {game['time']}\n"
    message = message.rstrip('\n')
    return message

if __name__ == "__main__":
    raw_games = fetch_warriors_schedule()
    upcoming_games = filter_upcoming_games(raw_games)
    message = format_schedule_message(upcoming_games)
    print(message)