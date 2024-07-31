import requests
import csv
import os

# Load API credentials from the README file
API_TOKEN = '12abfbaacdab48bc8948ed6061925e1f'
BASE_URL = 'https://api.football-data.org/v2/'

HEADERS = {'X-Auth-Token': API_TOKEN}

def fetch_team_data(year):
    endpoint = f'{BASE_URL}competitions/PL/matches'
    params = {
        'season': year
    }
    response = requests.get(endpoint, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()


def transform_data(raw_data):
    teams_stats = {}
    
    for match in raw_data['matches']:
        season = match['season']['startDate'][:4]
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        
        if home_team not in teams_stats:
            teams_stats[home_team] = {'won': 0, 'drawn': 0, 'lost': 0, 'goals_for': 0, 'goals_against': 0, 'year': season}
        if away_team not in teams_stats:
            teams_stats[away_team] = {'won': 0, 'drawn': 0, 'lost': 0, 'goals_for': 0, 'goals_against': 0, 'year': season}

        if match['score']['winner'] == 'HOME_TEAM':
            teams_stats[home_team]['won'] += 1
            teams_stats[away_team]['lost'] += 1
        elif match['score']['winner'] == 'AWAY_TEAM':
            teams_stats[away_team]['won'] += 1
            teams_stats[home_team]['lost'] += 1
        else:
            teams_stats[home_team]['drawn'] += 1
            teams_stats[away_team]['drawn'] += 1

        teams_stats[home_team]['goals_for'] += match['score']['fullTime']['homeTeam']
        teams_stats[home_team]['goals_against'] += match['score']['fullTime']['awayTeam']
        teams_stats[away_team]['goals_for'] += match['score']['fullTime']['awayTeam']
        teams_stats[away_team]['goals_against'] += match['score']['fullTime']['homeTeam']
    
    return teams_stats

def save_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Year', 'Team', 'Won', 'Drawn', 'Lost', 'Goals For', 'Goals Against'])
        
        for team, stats in data.items():
            writer.writerow([
                stats['year'], team, stats['won'], stats['drawn'], stats['lost'],
                stats['goals_for'], stats['goals_against']
            ])

if __name__ == "__main__":
    all_data = {}
    for year in range(2020, 2024):
        raw_data = fetch_team_data(year)
        yearly_data = transform_data(raw_data)
        all_data.update(yearly_data)
    
    save_to_csv(all_data, 'epl_team_performance.csv')
