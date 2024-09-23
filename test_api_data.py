import pytest
from unittest.mock import patch
from api_data import extract_api_data

@pytest.fixture
def mock_api_response():
    mock_data = {
        "filters": {
            "season": "2024"
        },
        "area": {
            "id": 2072,
            "name": "England",
            "code": "ENG",
            "flag": "https://crests.football-data.org/770.svg"
        },
        "competition": {
            "id": 2021,
            "name": "Premier League",
            "code": "PL",
            "type": "LEAGUE",
            "emblem": "https://crests.football-data.org/PL.png"
        },
        "season": {
            "id": 2287,
            "startDate": "2024-08-16",
            "endDate": "2025-05-25",
            "currentMatchday": 5,
            "winner": None
        },
        "standings": [
            {
                "stage": "REGULAR_SEASON",
                "type": "TOTAL",
                "group": None,
                "table": [
                    {
                        "position": 1,
                        "team": {
                            "id": 65,
                            "name": "Manchester City FC",
                            "shortName": "Man City",
                            "tla": "MCI",
                            "crest": "https://crests.football-data.org/65.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 4,
                        "draw": 1,
                        "lost": 0,
                        "points": 13,
                        "goalsFor": 13,
                        "goalsAgainst": 5,
                        "goalDifference": 8
                    },
                    {
                        "position": 2,
                        "team": {
                            "id": 64,
                            "name": "Liverpool FC",
                            "shortName": "Liverpool",
                            "tla": "LIV",
                            "crest": "https://crests.football-data.org/64.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 4,
                        "draw": 0,
                        "lost": 1,
                        "points": 12,
                        "goalsFor": 10,
                        "goalsAgainst": 1,
                        "goalDifference": 9
                    },
                    {
                        "position": 3,
                        "team": {
                            "id": 58,
                            "name": "Aston Villa FC",
                            "shortName": "Aston Villa",
                            "tla": "AVL",
                            "crest": "https://crests.football-data.org/58.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 4,
                        "draw": 0,
                        "lost": 1,
                        "points": 12,
                        "goalsFor": 10,
                        "goalsAgainst": 7,
                        "goalDifference": 3
                    },
                    {
                        "position": 4,
                        "team": {
                            "id": 57,
                            "name": "Arsenal FC",
                            "shortName": "Arsenal",
                            "tla": "ARS",
                            "crest": "https://crests.football-data.org/57.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 3,
                        "draw": 2,
                        "lost": 0,
                        "points": 11,
                        "goalsFor": 8,
                        "goalsAgainst": 3,
                        "goalDifference": 5
                    },
                    {
                        "position": 5,
                        "team": {
                            "id": 61,
                            "name": "Chelsea FC",
                            "shortName": "Chelsea",
                            "tla": "CHE",
                            "crest": "https://crests.football-data.org/61.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 3,
                        "draw": 1,
                        "lost": 1,
                        "points": 10,
                        "goalsFor": 11,
                        "goalsAgainst": 5,
                        "goalDifference": 6
                    },
                    {
                        "position": 6,
                        "team": {
                            "id": 67,
                            "name": "Newcastle United FC",
                            "shortName": "Newcastle",
                            "tla": "NEW",
                            "crest": "https://crests.football-data.org/67.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 3,
                        "draw": 1,
                        "lost": 1,
                        "points": 10,
                        "goalsFor": 7,
                        "goalsAgainst": 6,
                        "goalDifference": 1
                    },
                    {
                        "position": 7,
                        "team": {
                            "id": 397,
                            "name": "Brighton & Hove Albion FC",
                            "shortName": "Brighton Hove",
                            "tla": "BHA",
                            "crest": "https://crests.football-data.org/397.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 2,
                        "draw": 3,
                        "lost": 0,
                        "points": 9,
                        "goalsFor": 8,
                        "goalsAgainst": 4,
                        "goalDifference": 4
                    },
                    {
                        "position": 8,
                        "team": {
                            "id": 351,
                            "name": "Nottingham Forest FC",
                            "shortName": "Nottingham",
                            "tla": "NOT",
                            "crest": "https://crests.football-data.org/351.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 2,
                        "draw": 3,
                        "lost": 0,
                        "points": 9,
                        "goalsFor": 6,
                        "goalsAgainst": 4,
                        "goalDifference": 2
                    },
                    {
                        "position": 9,
                        "team": {
                            "id": 63,
                            "name": "Fulham FC",
                            "shortName": "Fulham",
                            "tla": "FUL",
                            "crest": "https://crests.football-data.org/63.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 2,
                        "draw": 2,
                        "lost": 1,
                        "points": 8,
                        "goalsFor": 7,
                        "goalsAgainst": 5,
                        "goalDifference": 2
                    },
                    {
                        "position": 10,
                        "team": {
                            "id": 73,
                            "name": "Tottenham Hotspur FC",
                            "shortName": "Tottenham",
                            "tla": "TOT",
                            "crest": "https://crests.football-data.org/73.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 2,
                        "draw": 1,
                        "lost": 2,
                        "points": 7,
                        "goalsFor": 9,
                        "goalsAgainst": 5,
                        "goalDifference": 4
                    },
                    {
                        "position": 11,
                        "team": {
                            "id": 66,
                            "name": "Manchester United FC",
                            "shortName": "Man United",
                            "tla": "MUN",
                            "crest": "https://crests.football-data.org/66.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 2,
                        "draw": 1,
                        "lost": 2,
                        "points": 7,
                        "goalsFor": 5,
                        "goalsAgainst": 5,
                        "goalDifference": 0
                    },
                    {
                        "position": 12,
                        "team": {
                            "id": 402,
                            "name": "Brentford FC",
                            "shortName": "Brentford",
                            "tla": "BRE",
                            "crest": "https://crests.football-data.org/402.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 2,
                        "draw": 0,
                        "lost": 3,
                        "points": 6,
                        "goalsFor": 7,
                        "goalsAgainst": 9,
                        "goalDifference": -2
                    },
                    {
                        "position": 13,
                        "team": {
                            "id": 1044,
                            "name": "AFC Bournemouth",
                            "shortName": "Bournemouth",
                            "tla": "BOU",
                            "crest": "https://crests.football-data.org/bournemouth.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 1,
                        "draw": 2,
                        "lost": 2,
                        "points": 5,
                        "goalsFor": 5,
                        "goalsAgainst": 8,
                        "goalDifference": -3
                    },
                    {
                        "position": 14,
                        "team": {
                            "id": 563,
                            "name": "West Ham United FC",
                            "shortName": "West Ham",
                            "tla": "WHU",
                            "crest": "https://crests.football-data.org/563.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 1,
                        "draw": 1,
                        "lost": 3,
                        "points": 4,
                        "goalsFor": 5,
                        "goalsAgainst": 9,
                        "goalDifference": -4
                    },
                    {
                        "position": 15,
                        "team": {
                            "id": 338,
                            "name": "Leicester City FC",
                            "shortName": "Leicester City",
                            "tla": "LEI",
                            "crest": "https://crests.football-data.org/338.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 0,
                        "draw": 3,
                        "lost": 2,
                        "points": 3,
                        "goalsFor": 6,
                        "goalsAgainst": 8,
                        "goalDifference": -2
                    },
                    {
                        "position": 16,
                        "team": {
                            "id": 354,
                            "name": "Crystal Palace FC",
                            "shortName": "Crystal Palace",
                            "tla": "CRY",
                            "crest": "https://crests.football-data.org/354.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 0,
                        "draw": 3,
                        "lost": 2,
                        "points": 3,
                        "goalsFor": 4,
                        "goalsAgainst": 7,
                        "goalDifference": -3
                    },
                    {
                        "position": 17,
                        "team": {
                            "id": 349,
                            "name": "Ipswich Town FC",
                            "shortName": "Ipswich Town",
                            "tla": "IPS",
                            "crest": "https://crests.football-data.org/349.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 0,
                        "draw": 3,
                        "lost": 2,
                        "points": 3,
                        "goalsFor": 3,
                        "goalsAgainst": 8,
                        "goalDifference": -5
                    },
                    {
                        "position": 18,
                        "team": {
                            "id": 340,
                            "name": "Southampton FC",
                            "shortName": "Southampton",
                            "tla": "SOU",
                            "crest": "https://crests.football-data.org/340.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 0,
                        "draw": 1,
                        "lost": 4,
                        "points": 1,
                        "goalsFor": 2,
                        "goalsAgainst": 9,
                        "goalDifference": -7
                    },
                    {
                        "position": 19,
                        "team": {
                            "id": 62,
                            "name": "Everton FC",
                            "shortName": "Everton",
                            "tla": "EVE",
                            "crest": "https://crests.football-data.org/62.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 0,
                        "draw": 1,
                        "lost": 4,
                        "points": 1,
                        "goalsFor": 5,
                        "goalsAgainst": 14,
                        "goalDifference": -9
                    },
                    {
                        "position": 19,
                        "team": {
                            "id": 76,
                            "name": "Wolverhampton Wanderers FC",
                            "shortName": "Wolverhampton",
                            "tla": "WOL",
                            "crest": "https://crests.football-data.org/76.png"
                        },
                        "playedGames": 5,
                        "form": None,
                        "won": 0,
                        "draw": 1,
                        "lost": 4,
                        "points": 1,
                        "goalsFor": 5,
                        "goalsAgainst": 14,
                        "goalDifference": -9
                    }
                ]
            }
        ]
    }
    return mock_data

def test_fetch_data_success(mock_api_response):
    
    api_url = "https://api.football-data.org/v4/competitions/PL/standings"
    headers = {'X-Auth-Token': '12abfbaacdab48bc8948ed6061925e1f'}

    with patch('requests.get') as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_api_response
        mock_get.return_value.status_code = 200

        response = extract_api_data('2024')
        
        assert response == mock_api_response
        
        mock_get.assert_called_once_with(api_url, params={'season':"2024"}, headers=headers)
