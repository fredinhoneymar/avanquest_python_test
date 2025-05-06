import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
headers = {'X-Auth-Token': API_TOKEN}

response = requests.get("https://api.football-data.org/v4/competitions/PL/matches?season=2023", headers=headers)
data = response.json()

# Save the data to a JSON file to inspect the structure
with open('query_example.json', 'w') as f:
    json.dump(data, f, indent=4)