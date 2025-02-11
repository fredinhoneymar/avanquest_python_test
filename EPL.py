import requests
import pandas as pd

# API credentials
API_TOKEN = "12abfbaacdab48bc8948ed6061925e1f"
BASE_URL = "https://api.football-data.org/v4/competitions/PL/standings"
HEADERS = {"X-Auth-Token": API_TOKEN}

# Seasons to fetch
seasons = [2020, 2021, 2022, 2023]
all_data = []

for season in seasons:
    params = {"season": season}
    response = requests.get(BASE_URL, headers=HEADERS, params=params)

    if response.status_code == 200:
        data = response.json()
        standings = data.get("standings", [])[0].get("table", [])

        for team in standings:
            all_data.append({
                "Season": season,
                "Position": team["position"],
                "Team": team["team"]["name"],
                "Played": team["playedGames"],
                "Won": team["won"],
                "Drawn": team["draw"],
                "Lost": team["lost"],
                "Goals For": team["goalsFor"],
                "Goals Against": team["goalsAgainst"],
                "Goal Difference": team["goalDifference"],
                "Points": team["points"]
            })
    else:
        print(f"Failed to fetch data for season {season}. Status Code: {response.status_code}")

# Convert to DataFrame and save as CSV
df = pd.DataFrame(all_data)
df.to_csv("EPL_Standings_2020_2023.csv", index=False)

print("Data saved to EPL_Standings_2020_2023.csv")
