import unittest
from DATAFETCH import fetch_team_data, transform_data

class TestFetchData(unittest.TestCase):

    def test_fetch_team_data(self):
        # This test requires actual API call, so consider mocking the request
        data = fetch_team_data(2020)
        self.assertIn('matches', data)

    def test_transform_data(self):
        raw_data = {
            'matches': [
                {
                    'season': {'startDate': '2020-08-01'},
                    'homeTeam': {'name': 'Team A'},
                    'awayTeam': {'name': 'Team B'},
                    'score': {'fullTime': {'homeTeam': 2, 'awayTeam': 1}, 'winner': 'HOME_TEAM'}
                },
                {
                    'season': {'startDate': '2020-08-01'},
                    'homeTeam': {'name': 'Team B'},
                    'awayTeam': {'name': 'Team A'},
                    'score': {'fullTime': {'homeTeam': 1, 'awayTeam': 1}, 'winner': 'DRAW'}
                }
            ]
        }
        transformed_data = transform_data(raw_data)
        self.assertEqual(transformed_data['Team A']['won'], 1)
        self.assertEqual(transformed_data['Team A']['drawn'], 1)
        self.assertEqual(transformed_data['Team A']['goals_for'], 3)
        self.assertEqual(transformed_data['Team A']['goals_against'], 2)

if __name__ == '__main__':
    unittest.main()