import unittest
from unittest.mock import patch, MagicMock
import os
import pandas as pd

from EPL1 import fetch_standings, parse_standings, main

class TestFootballStandings(unittest.TestCase):

    @patch("requests.get")
    def test_fetch_standings_success(self, mock_get):
        #Test API fetch with a valid response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "standings": [{
                "table": [
                    {
                        "position": 1,
                        "team": {"name": "Team A"},
                        "playedGames": 38,
                        "won": 30,
                        "draw": 5,
                        "lost": 3,
                        "goalsFor": 90,
                        "goalsAgainst": 30,
                        "goalDifference": 60,
                        "points": 95
                    },
                    {
                        "position": 2,
                        "team": {"name": "Team B"},
                        "playedGames": 38,
                        "won": 28,
                        "draw": 6,
                        "lost": 4,
                        "goalsFor": 85,
                        "goalsAgainst": 35,
                        "goalDifference": 50,
                        "points": 90
                    }
                ]
            }]
        }
        mock_get.return_value = mock_response

        data = fetch_standings(2023)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["Team"], "Team A")
        self.assertEqual(data[1]["Points"], 90)

    @patch("requests.get")
    def test_fetch_standings_empty(self, mock_get):
        #Test API response with no standings
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"standings": []}
        mock_get.return_value = mock_response

        data = fetch_standings(2023)
        self.assertEqual(data, [])

    @patch("requests.get")
    def test_fetch_standings_invalid_token(self, mock_get):
        #Test API response with invalid token
        mock_response = MagicMock()
        mock_response.status_code = 403  # Forbidden
        mock_response.json.return_value = {"message": "Invalid API token"}
        mock_get.return_value = mock_response

        data = fetch_standings(2023)
        self.assertEqual(data, [])

    @patch("requests.get")
    def test_fetch_standings_server_error(self, mock_get):
        #Test API server error (500)
        mock_response = MagicMock()
        mock_response.status_code = 500  # Internal Server Error
        mock_get.return_value = mock_response

        data = fetch_standings(2023)
        self.assertEqual(data, [])

    def test_parse_standings(self):
        #Test parsing function with multiple teams
        sample_data = [
            {
                "position": 1,
                "team": {"name": "Team X"},
                "playedGames": 38,
                "won": 29,
                "draw": 5,
                "lost": 4,
                "goalsFor": 88,
                "goalsAgainst": 32,
                "goalDifference": 56,
                "points": 92
            },
            {
                "position": 2,
                "team": {"name": "Team Y"},
                "playedGames": 38,
                "won": 27,
                "draw": 7,
                "lost": 4,
                "goalsFor": 81,
                "goalsAgainst": 37,
                "goalDifference": 44,
                "points": 88
            }
        ]
        parsed_data = parse_standings(2023, sample_data)
        self.assertEqual(len(parsed_data), 2)
        self.assertEqual(parsed_data[0]["Team"], "Team X")
        self.assertEqual(parsed_data[1]["Points"], 88)

    def test_csv_file_creation(self):
        #Test if CSV file is created successfully by running main()
        filename = "EPL_Standings_2020_2023.csv"

        main()

        # Verify the file is created
        self.assertTrue(os.path.exists(filename), f"Expected file {filename} not found!")

        # Read CSV and verify content
        df = pd.read_csv(filename)
        self.assertGreater(df.shape[0], 0, "CSV file should have at least one row!")

if __name__ == "__main__":
    unittest.main()
