# test
football
API:

API initial Url: https://api.football-data.org/

API account name: testing.data999@gmail.com

API token information:

Please modify your client to use a HTTP header named "X-Auth-Token" with the underneath personal token as value. Your token: 12abfbaacdab48bc8948ed6061925e1f

# notes
While using the API I noticed that the above token does not give me access to seasons prior to 2023.
So for this test instead of querying 2020-2023, I only queried 2023-2024.

- pytest.ini used to fix some issues caused by a space in my folder names
- Unit tests are provided in the tests/ folder
- All external API calls are mocked for consistent, offline test run
- example.py is used to get query_example.json which gave me the API dictionnary format
- Token stored in .env (.gitignore)
- example.py used to inspect the structure of the API response
- Outputs: match_raw_data.csv and match_team_stats.csv
- argparse used for CLI flexibility (--seasons) with default: --seasons 2023 2024 the only accessible seasons with this token.
