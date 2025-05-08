import requests
from config.settings import API_TOKEN, BASE_URL
from config.logging_config import setup_logger

# Header used for authenticating requests to the API
HEADERS = {"X-Auth-Token": API_TOKEN}

def get_matches(season_year, logger):
    """Fetches Premier League matches for the specified season year."""
    url = f"{BASE_URL}/competitions/PL/matches?season={season_year}"
    logger.info(f" Fetching data for season {season_year}...")

    try:
        # Perform GET request to fetch match data
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Log any error that occurs during the request
        logger.error(f" Request error for season {season_year}: {e}")
        return []
    # Parse JSON response and return the list of matches
    matches = response.json().get("matches", [])
    logger.info(f" {len(matches)} matches received for season {season_year}")
    return matches
