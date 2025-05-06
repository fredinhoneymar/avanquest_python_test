from dotenv import load_dotenv
import os
import requests
import pandas as pd
import argparse
from typing import List, Dict

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
HEADERS = {'X-Auth-Token': API_TOKEN}
URL = 'https://api.football-data.org/v4/competitions/PL/matches'

def fetch_matches_for_season(season: int) -> List[Dict]:
    """
    Fetch matches for a given season from the football-data.org API.
    
    Args:
        season (int): The season year to fetch matches for.
        
    Returns:
        List[Dict]: A list of match dictionaries.
    """
    url = f"{URL}?season={season}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise Exception(f"Error fetching data for {season}: {response.status_code} - {response.text}")
    
    data = response.json().get('matches', [])
    # We query the API for all matches in a season
    return [
        {
            "season": season,
            "date": m["utcDate"][:10],
            "matchday": m.get("matchday"),
            "hometeam": m["homeTeam"]["name"],
            "awayteam": m["awayTeam"]["name"],
            "homeGoals": m["score"]["fullTime"]["home"],
            "awayGoals": m["score"]["fullTime"]["away"],
            "winner": m["score"]["winner"],
        }
        for m in data if m["status"] == "FINISHED" # Only include finished matches
    ]

def fetch_all_seasons(seasons: List[int]) -> pd.DataFrame:
    """
    Fetch matches for multiple seasons and return as a DataFrame.
    
    Args:
        seasons (List[int]): A list of season years to fetch matches for.
        
    Returns:
        pd.DataFrame: A DataFrame containing all matches for the given seasons.
    """
    all_matches = []
    for year in seasons:
        print(f"Fetching matches for season {year}...")
        matches = fetch_matches_for_season(year)
        all_matches.extend(matches)
    
    return pd.DataFrame(all_matches)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the DataFrame to a team-level KPI summary per season.
    
    Args:
        df (pd.DataFrame): The DataFrame to transform (match level data).
        
    Returns:
        pd.DataFrame: The transformed DataFrame: aggregated team KPIs per season.
    """
    records = []
    # For each match, create records for both home and away teams
    for _, row in df.iterrows():
        # Create a record for the home team
        records.append({
            "season": row["season"],
            "team": row["hometeam"],
            "played": 1,
            "won": int(row["winner"] == "HOME_TEAM"),
            "drawn": int(row["winner"] is None),
            "lost": int(row["winner"] == "AWAY_TEAM"),
            "goals for": row["homeGoals"],
            "goals against": row["awayGoals"],
        })
        # Create a record for the away team
        records.append({
            "season": row["season"],
            "team": row["awayteam"],
            "played": 1,
            "won": int(row["winner"] == "AWAY_TEAM"),
            "drawn": int(row["winner"] is None),
            "lost": int(row["winner"] == "HOME_TEAM"),
            "goals for": row["awayGoals"],
            "goals against": row["homeGoals"],
        })

    df_teams = pd.DataFrame(records)
    # Aggregate the data to get team-level KPIs per season
    df_summary = df_teams.groupby(["season", "team"], as_index=False).sum()
    return df_summary

def main(seasons: List[int]): 
    """
    Main function to fetch and save football match data.
    
    Args:
        seasons (List[int]): A list of season years to fetch matches for.
    """
    df_raw = fetch_all_seasons(seasons)
    df_teams = transform_data(df_raw)
    # Save the DataFrame to a CSV file
    df_teams.to_csv('match_team_stats.csv', index=False)
    df_raw.to_csv('match_raw_data.csv', index=False)
    print("Data saved to match_team_stats.csv and match_raw_data.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch football match data for specified seasons.")
    parser.add_argument(
        '--seasons', 
        type=int, 
        nargs='+', 
        default=[2023, 2024], 
        help='List of seasons to fetch data for (default: 2023, 2024)')  # We dont have access to data prior to 2023 on this API subscription plan
    args = parser.parse_args()
    main(args.seasons)

