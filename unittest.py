import unittest
from unittest.mock import patch
from fetch_football_data import fetch_data, get_epl_matches, calculate_kpis


class TestFetchFootballData(unittest.TestCase):

    @patch('fetch_football_data.requests.get')
    def test_fetch_data(self, mock_get):
        # Mock the API response
        mock_get.return_value.json.return_value = {'matches': 'test_data'}
        result = fetch_data('competitions/2021/matches', {'season': 2023})

        self.assertIn('matches', result)
        self.assertEqual(result['matches'], 'test_data')

    @patch('fetch_football_data.fetch_data')
    def test_get_epl_matches(self, mock_fetch_data):
        # Mock the fetch_data function
        mock_fetch_data.return_value = {'matches': [{'homeTeam': {'name': 'Team A'}, 'awayTeam': {'name': 'Team B'},
                                                     'score': {'fullTime': {'home': 1, 'away': 2}}}]}

        result = get_epl_matches(2023)
        self.assertIsInstance(result, dict)
        self.assertIn('matches', result)

    def test_calculate_kpis(self):
        # Sample match data
        sample_matches = [
            {
                'homeTeam': {'name': 'Team A'},
                'awayTeam': {'name': 'Team B'},
                'score': {'fullTime': {'home': 3, 'away': 1}}
            },
            {
                'homeTeam': {'name': 'Team A'},
                'awayTeam': {'name': 'Team C'},
                'score': {'fullTime': {'home': 2, 'away': 2}}
            },
            {
                'homeTeam': {'name': 'Team B'},
                'awayTeam': {'name': 'Team A'},
                'score': {'fullTime': {'home': 1, 'away': 2}}
            }
        ]

        result = list(calculate_kpis(sample_matches))

        self.assertEqual(len(result), 3)

        team_a = next(item for item in result if item['team'] == 'Team A')
        self.assertEqual(team_a['won'], 2)
        self.assertEqual(team_a['drawn'], 1)
        self.assertEqual(team_a['lost'], 0)
        self.assertEqual(team_a['goals_for'], 7)
        self.assertEqual(team_a['goals_against'], 4)


if __name__ == '__main__':
    unittest.main()
