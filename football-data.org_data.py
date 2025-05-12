import requests
import pandas as pd

competitions_url = "https://api.football-data.org/v4/competitions/"
headers = {"X-Auth-Token": "12abfbaacdab48bc8948ed6061925e1f"}

response = requests.get(competitions_url, headers=headers)
competitions = response.json()

# Return all IDs from all competitions
print("Available competitions:")
for competition in competitions['competitions']:
    print(f"competition name: {competition['name']} | ID: {competition['code']}")

# Retrieve all PL games from a specific season
id = 'PL'
season = '2023'
game_url = f"https://api.football-data.org/v4/competitions/{id}/matches?season={season}"
response = requests.get(game_url, headers=headers)
game_data = response.json()

# Return all team stats
team_stats = {}

# Loop through each completed game
for match in game_data['matches']:
    if match['status'] != 'FINISHED':
        continue

    # Get the name of the home team, the away team, the goals scored by each, and the results
    home_team = match['homeTeam']['name']
    away_team = match['awayTeam']['name']
    home_goals = match['score']['fullTime']['home']
    away_goals = match['score']['fullTime']['away']
    winner = match['score']['winner']
    
    # Check if each team already exists. If not, initialize
    for team in [home_team, away_team]:
        if team not in team_stats:
            team_stats[team] = {'won': 0, 'drawn': 0, 'lost': 0, 'goals for': 0, 'goals against': 0}
    
    # Update stats
    team_stats[home_team]['goals for'] += home_goals
    team_stats[home_team]['goals against'] += away_goals
    
    team_stats[away_team]['goals for'] += away_goals
    team_stats[away_team]['goals against'] += home_goals
    
    if winner == 'HOME_TEAM':
        team_stats[home_team]['won'] += 1
        team_stats[away_team]['lost'] += 1
    elif winner == 'AWAY_TEAM':
        team_stats[away_team]['won'] += 1
        team_stats[home_team]['lost'] += 1
    else:
        team_stats[home_team]['drawn'] += 1
        team_stats[away_team]['drawn'] += 1

df = pd.DataFrame.from_dict(team_stats, orient='index')
df.reset_index(inplace=True)
df.rename(columns={'index': 'team name'}, inplace=True)

print(df.to_string())

df.to_csv("premier_league_2023_2024_stats.csv")