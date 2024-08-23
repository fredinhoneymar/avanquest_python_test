import requests
import csv
from collections import defaultdict

API_KEY = '12abfbaacdab48bc8948ed6061925e1f'
BASE_URL = 'https://api.football-data.org/v4/'


def fetch_data(endpoint, params=None):
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(BASE_URL + endpoint, headers=headers, params=params,verify=False)
    return response.json()

#fetching data of 2021
def get_epl_matches(season):
    endpoint = f'competitions/2021/matches'  # 2021 is the EPL competition ID
    params = {'season': season}
    return fetch_data(endpoint, params)

#creating kpis
def calculate_kpis(matches):
    kpis = defaultdict(lambda: {
        'team': '',
        'won': 0,
        'drawn': 0,
        'lost': 0,
        'goals_for': 0,
        'goals_against': 0
    })

    for match in matches:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        home_goals = match['score']['fullTime']['home']
        away_goals = match['score']['fullTime']['away']

        # Update goals for and against
        kpis[home_team]['team'] = home_team
        kpis[home_team]['goals_for'] += home_goals
        kpis[home_team]['goals_against'] += away_goals

        kpis[away_team]['team'] = away_team
        kpis[away_team]['goals_for'] += away_goals
        kpis[away_team]['goals_against'] += home_goals

        # Update won, drawn, lost
        if home_goals > away_goals:
            kpis[home_team]['won'] += 1
            kpis[away_team]['lost'] += 1
        elif home_goals < away_goals:
            kpis[away_team]['won'] += 1
            kpis[home_team]['lost'] += 1
        else:
            kpis[home_team]['drawn'] += 1
            kpis[away_team]['drawn'] += 1

    return kpis.values()


def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


if __name__ == "__main__":
    all_kpis = []
    for year in [2020, 2021, 2022, 2023]:
        matches = get_epl_matches(year)['matches']
        kpis = calculate_kpis(matches)
        for kpi in kpis:
            kpi['season'] = year
        all_kpis.extend(kpis)

    save_to_csv(all_kpis, 'C:\\Users\\kdalal\\epl_kpis_2020_2023.csv')
