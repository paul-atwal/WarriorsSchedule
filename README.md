# Warriors Schedule App

A mobile-first, spoiler-free schedule for the Golden State Warriors, built for watching in Surrey, BC.

## Screens

- **Home**: tells you when the next game is and where to watch it. The top card changes with the clock: a countdown on the days before, a gold "Tonight" card on game day, a scoreless "In progress" card during the game, then "Highlights ready" once it's final. Below that are the last game's highlights and the next four games, with each team's record.
- **Schedule**: the upcoming games grouped by month, each with the opponent's record and its TELUS channel, a crossed-out TV when it isn't on, or "TBA" before listings are out. The **Previous** tab lists final scores, with a highlights button on every game.
- **Game preview**: tip-off time, channel, arena, the season series (preseason included) and the opponent's top scorers.
- **Standings**: West and East, split into Playoffs (1–6), Play-in (7–10) and Lottery, with the Warriors highlighted. Until opening night it shows last season's final standings.
- **News**: Curry's status, the Warriors injury report and recent Warriors stories from ESPN.

Scores stay hidden unless you ask for them: tap the eye on Home's Last game card, or "Show live score" / "Show final score" on game day. The **Previous** tab shows scores, since opening it is the choice to see results.

## Data

`backend/generate_data.py` runs daily from GitHub Actions and writes `backend/data/`:

- `schedule.json`: the full season from ESPN, plus the TELUS Optik TV channel for each game from Gracenote's listings for Surrey. NBA TV-only games count as "No TV". Listings run about two weeks ahead, so games further out show "TV TBA".
- `standings.json`: conference standings from ESPN. ESPN's current-season numbers include preseason games, so until the regular season starts this holds last season's final standings.
- `team_details.json`: every team's current record and each opponent's top three scorers. Scorers stay empty until the regular season has stats.
- `news.json`: the ESPN injury report and Warriors-only news. Video clips are left out so highlights don't spoil results.

The Flask API (`backend/app.py`) serves those files. `/api/score/<id>` fetches a live or final score from ESPN, but only when you ask to see it.

## Tech Stack

- **Frontend**: React, Vite, React Router.
- **Backend**: Python, Flask, `requests`.

## Running Locally

1. **Backend**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python generate_data.py   # optional: refresh the data
   python app.py
   ```

2. **Frontend**:
   ```bash
   npm install
   npm run dev
   ```

During development you can add `?now=2026-10-21T18:00:00-07:00` to the URL to pretend it's a different time and check the game-day states on Home.

## Deployment

This project is configured for deployment on **Vercel** (see `vercel.json`).
