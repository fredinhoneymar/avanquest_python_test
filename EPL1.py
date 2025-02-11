import requests
import pandas as pd
from typing import List, Dict, Any

# API credentials
API_TOKEN = "12abfbaacdab48bc8948ed6061925e1f"
BASE_URL = "https://api.football-data.org/v4/competitions/PL/standings"
HEADERS = {"X-Auth-Token": API_TOKEN}
SEASONS = [2020, 2021, 2022, 2023]

def fetch_standings(season: int) -> List[Dict[str, Any]]:

    #Fetches EPL standings for a given season.
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params={"season": season})
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Ensure standings exist before accessing index 0
        standings_list = data.get("standings", [])
        if not standings_list:
            return []  # Return empty list if no standings are found

        standings = standings_list[0].get("table", [])
        return parse_standings(season, standings)

    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return []

def parse_standings(season: int, standings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    #Parses raw API standings data into a structured format.
    return [
        {
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
        }
        for team in standings
    ]

def main():
    #Main function to fetch, process, and save EPL standings data.
    all_data = []

    for season in SEASONS:
        all_data.extend(fetch_standings(season))

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("EPL_Standings_optimized_2020_2023.csv", index=False)
        print("Data saved to EPL_Standings_optimized_2020_2023.csv")
    else:
        print("No data available to save.")

if __name__ == "__main__":
    main()
