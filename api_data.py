import requests
import pandas as pd

base_url = 'https://api.football-data.org/v4/competitions/PL/standings'
headers = {'X-Auth-Token': '12abfbaacdab48bc8948ed6061925e1f'}
seasons = [2022, 2023, 2024]
dfs = list()

def extract_api_data(season):
    try:
        result = requests.get(base_url, headers=headers, params = {"season": season})
        data = result.json()
        return data
    except Exception as Err:
        print(f"Error while fetching API data {Err}")
    return None

def transform_dataframe(standing, season):
    column_names = ["team.name", "won", "draw", "lost", "goalsFor", "goalsAgainst"]
    if standing.get("type", "") == 'TOTAL':
        df = pd.json_normalize(standing["table"])
        df = df[column_names]
        df['Year'] = season
        dfs.append(df)

def load_data(dfs):
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.to_csv(f"EPL_competition_data.csv",index = False)

if __name__ == '__main__':
    for season in seasons:
        data = extract_api_data(season)
        for standing in data.get("standings", []):
            transform_dataframe(standing, season)
        load_data(dfs)
