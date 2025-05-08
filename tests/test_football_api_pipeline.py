import requests
import logging
import csv
import os
from unittest.mock import patch, MagicMock
import unittest

# Function to fetch Premier League matches
def get_matches(season_year, logger):
    """Fetches Premier League matches for the specified season"""
    url = f"https://api.football-data.org/v2/competitions/PL/matches?season={season_year}"
    logger.info(f"Fetching data for season {season_year}...")

    try:
        response = requests.get(url, headers={"X-Auth-Token": "seu_token_aqui"})
        response.raise_for_status()  # Checks if the request returned an HTTP error
        matches = response.json().get('matches', [])
        logger.info(f"{len(matches)} matches received for {season_year}")
        return matches
    except Exception as e:
        logger.error(f"Request error for season {season_year}: {str(e)}")
        return []  # Returns an empty list in case of error
    

# Function to process the matches
def process_matches(matches, logger):
    """Processes match data to extract relevant information"""
    teams = set()  # Using a set to ensure unique teams
    for match in matches:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        teams.add(home_team)
        teams.add(away_team)

    logger.info(f"Processed data: {len(teams)} teams")
    return teams


# Function to save data to a CSV file
def save_to_csv(teams, season_year, logger):
    """Saves team data to a CSV file"""
    file_name = f"./output/epl_stats_{season_year}.csv"
    
    # Ensures the output directory exists
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Team'])
        for team in teams:
            writer.writerow([team])
    logger.info(f"File saved: {file_name}")


# Main function that runs the full pipeline
def run_pipeline_for_year(season_year, logger):
    """Runs the complete data retrieval and processing pipeline"""
    matches = get_matches(season_year, logger)
    if matches:
        teams = process_matches(matches, logger)
        save_to_csv(teams, season_year, logger)


# Test Class
class TestApiClient(unittest.TestCase):

    @patch("requests.get")  # Mock for the requests.get function
    @patch("logging.getLogger")  # Mock for the logger
    def test_get_matches_failure(self, mock_logger, mock_get):
        """Tests failure scenario when requesting matches"""
        
        # Simulate request failure by raising a custom exception
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        
        # Mock do logger
        mock_logger = MagicMock()
        mock_logger.return_value = mock_logger
        
        season_year = 2024
        
        # Call the function with the mocked logger
        matches = get_matches(season_year, mock_logger)
        
        # Assert logger was called with the correct error message
        mock_logger.error.assert_any_call(f"Request error for season {season_year}: Request failed")
        
        # Assert the result was an empty list (or the expected fallback value)
        self.assertEqual(matches, [])

    @patch("logging.getLogger")
    def test_run_pipeline_for_year(self, mock_logger):
        """Tests the main pipeline"""

        # Simulated input data
        mock_logger = MagicMock()
        season_year = 2024

        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                'matches': [
                    {'homeTeam': {'name': 'Team A'}, 'awayTeam': {'name': 'Team B'}},
                    {'homeTeam': {'name': 'Team A'}, 'awayTeam': {'name': 'Team C'}}
                ]
            }

            # Run the pipeline function
            run_pipeline_for_year(season_year, mock_logger)
            
            # Verify internal function calls via logger
            mock_logger.info.assert_any_call(f"Fetching data for season {season_year}...")
            mock_logger.info.assert_any_call(f"2 matches received for {season_year}")
            mock_logger.info.assert_any_call("Processed data: 3 teams")
            mock_logger.info.assert_any_call(f"File saved: ./output/epl_stats_{season_year}.csv")


if __name__ == "__main__":
    unittest.main()
