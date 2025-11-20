from nba_api.stats.static import teams

# Frontend map from src/utils/logos.js
frontend_map = {
    'Atlanta Hawks': 'atl',
    'Boston Celtics': 'bos',
    'Brooklyn Nets': 'bkn',
    'Charlotte Hornets': 'cha',
    'Chicago Bulls': 'chi',
    'Cleveland Cavaliers': 'cle',
    'Dallas Mavericks': 'dal',
    'Denver Nuggets': 'den',
    'Detroit Pistons': 'det',
    'Golden State Warriors': 'gsw',
    'Houston Rockets': 'hou',
    'Indiana Pacers': 'ind',
    'LA Clippers': 'lac',
    'Los Angeles Lakers': 'lal',
    'Memphis Grizzlies': 'mem',
    'Miami Heat': 'mia',
    'Milwaukee Bucks': 'mil',
    'Minnesota Timberwolves': 'min',
    'New Orleans Pelicans': 'nola',
    'New York Knicks': 'nyk',
    'Oklahoma City Thunder': 'okc',
    'Orlando Magic': 'orl',
    'Philadelphia 76ers': 'phi',
    'Phoenix Suns': 'phx',
    'Portland Trail Blazers': 'por',
    'Sacramento Kings': 'sac',
    'San Antonio Spurs': 'sas',
    'Toronto Raptors': 'tor',
    'Utah Jazz': 'utah',
    'Washington Wizards': 'was',
}

nba_teams = teams.get_teams()
print(f"Found {len(nba_teams)} teams in NBA API.")

missing = []
mismatch = []

for team in nba_teams:
    full_name = team['full_name']
    if full_name not in frontend_map:
        missing.append(full_name)
    else:
        # print(f"Matched: {full_name} -> {frontend_map[full_name]}")
        pass

print("\n--- Missing Teams ---")
for m in missing:
    print(m)

print("\n--- Frontend Map Keys ---")
for k in frontend_map.keys():
    found = False
    for team in nba_teams:
        if team['full_name'] == k:
            found = True
            break
    if not found:
        print(f"Key in frontend map NOT found in API: {k}")
