import pytest
from unittest.mock import patch, Mock
from match_stats.fetch_football_stats import fetch_matches_for_season, fetch_all_seasons
import pandas as pd

sample_response = {
    "matches": [
        {
            "utcDate": "2023-08-13T14:00:00Z",
            "matchday": 1,
            "homeTeam": {"name": "Team A"},
            "awayTeam": {"name": "Team B"},
            "score": {
                "fullTime": {"home": 2, "away": 1},
                "winner": "HOME_TEAM"
            },
            "status": "FINISHED"
        },
        {
            "utcDate": "2023-08-14T14:00:00Z",
            "matchday": 1,
            "homeTeam": {"name": "Team C"},
            "awayTeam": {"name": "Team D"},
            "score": {
                "fullTime": {"home": 0, "away": 0},
                "winner": None
            },
            "status": "FINISHED"
        }
    ]
}

@patch("match_stats.fetch_football_stats.requests.get")
def test_fetch_matches_for_season(mock_get):
    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_response
    mock_get.return_value = mock_response

    results = fetch_matches_for_season(2023)
    
    assert isinstance(results, list)
    assert len(results) == 2

    first = results[0]
    assert first["season"] == 2023
    assert first["hometeam"] == "Team A"
    assert first["awayteam"] == "Team B"
    assert first["homeGoals"] == 2
    assert first["awayGoals"] == 1
    assert first["winner"] == "HOME_TEAM"
    assert first["date"] == "2023-08-13"

    second = results[1]
    assert second["winner"] is None
    assert second["homeGoals"] == 0
    assert second["awayGoals"] == 0

@patch("match_stats.fetch_football_stats.fetch_matches_for_season")
def test_fetch_all_seasons(mock_fetch):
    mock_fetch.return_value = [
        {
            "season": 2023,
            "date": "2023-08-13",
            "matchday": 1,
            "hometeam": "Team A",
            "awayteam": "Team B",
            "homeGoals": 2,
            "awayGoals": 1,
            "winner": "HOME_TEAM"
        },
        {
            "season": 2023,
            "date": "2023-08-14",
            "matchday": 1,
            "hometeam": "Team C",
            "awayteam": "Team D",
            "homeGoals": 0,
            "awayGoals": 0,
            "winner": None
        }
    ]

    df = fetch_all_seasons([2023])

    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 2
    assert "hometeam" in df.columns
    assert df.loc[0, "hometeam"] == "Team A"
    assert df.loc[1, "awayGoals"] == 0

def test_transform_data():
    # Sample input: 4 matches across 2 seasons (6 total team-season rows expected)
    df = pd.DataFrame([
        # Season 2023
        {
            "season": 2023,
            "date": "2023-08-13",
            "matchday": 1,
            "hometeam": "Team A",
            "awayteam": "Team B",
            "homeGoals": 3,
            "awayGoals": 1,
            "winner": "HOME_TEAM"
        },
        {
            "season": 2023,
            "date": "2023-08-14",
            "matchday": 2,
            "hometeam": "Team B",
            "awayteam": "Team C",
            "homeGoals": 0,
            "awayGoals": 0,
            "winner": None
        },
        # Season 2024
        {
            "season": 2024,
            "date": "2024-08-13",
            "matchday": 1,
            "hometeam": "Team A",
            "awayteam": "Team C",
            "homeGoals": 1,
            "awayGoals": 2,
            "winner": "AWAY_TEAM"
        },
        {
            "season": 2024,
            "date": "2024-08-14",
            "matchday": 2,
            "hometeam": "Team B",
            "awayteam": "Team A",
            "homeGoals": 0,
            "awayGoals": 1,
            "winner": "AWAY_TEAM"
        }
    ])

    from match_stats.fetch_football_stats import transform_data
    df_kpi = transform_data(df)

    assert isinstance(df_kpi, pd.DataFrame)
    assert set(["season", "team", "played", "won", "drawn", "lost", "goals for", "goals against"]).issubset(df_kpi.columns)
    assert df_kpi.shape[0] == 6  # 4 matches = 8 team appearances grouped into 6 season-team entries

    # Check Team A in 2023: played 1, won 1
    team_a_2023 = df_kpi[(df_kpi["season"] == 2023) & (df_kpi["team"] == "Team A")].iloc[0]
    assert team_a_2023["played"] == 1
    assert team_a_2023["won"] == 1
    assert team_a_2023["goals for"] == 3
    assert team_a_2023["goals against"] == 1

    # Check Team A in 2024: played 2, lost 1, won 1
    team_a_2024 = df_kpi[(df_kpi["season"] == 2024) & (df_kpi["team"] == "Team A")].iloc[0]
    assert team_a_2024["played"] == 2
    assert team_a_2024["won"] == 1
    assert team_a_2024["lost"] == 1
    assert team_a_2024["goals for"] == 2
    assert team_a_2024["goals against"] == 2

    # Check Team C in 2024: played 1, won 1
    team_c_2024 = df_kpi[(df_kpi["season"] == 2024) & (df_kpi["team"] == "Team C")].iloc[0]
    assert team_c_2024["played"] == 1
    assert team_c_2024["won"] == 1
    assert team_c_2024["goals for"] == 2
    assert team_c_2024["goals against"] == 1

