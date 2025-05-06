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
- the API was mocked in the unit tests
- example.py is used to get query_example.json which gave me the API dictionnary format
- Token stored in .env