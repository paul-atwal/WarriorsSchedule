# Warriors Schedule App

A beautiful, spoiler-free schedule tracker for the Golden State Warriors.

## Features

-   **Next Game**: Shows the immediate next game with date, time (PST), and opponent.
-   **Last Game**: Displays the result of the most recent game with a "Watch Highlights" button linking to the official NBA.com game page.
-   **Schedule**: Lists upcoming games with opponent logos.
-   **Game Details**: Click on any game to see:
    -   Opponent's top scorers (with headshots).
    -   Head-to-head matchup history for the current season.
    -   Opponent's season record.
-   **Spoiler-Free**: Scores are only shown for past games.

## Tech Stack

-   **Frontend**: React, Vite, CSS (Glassmorphism UI).
-   **Backend**: Python, Flask, `nba_api`.

## Running Locally

1.  **Backend**:
    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python app.py
    ```

2.  **Frontend**:
    ```bash
    npm install
    npm run dev
    ```

## Deployment

This project is configured for easy deployment on **Vercel**.
See [deployment.md](deployment.md) for details.
