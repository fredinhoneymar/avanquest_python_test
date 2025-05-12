import unittest
import pandas as pd

class TestDataFrame(unittest.TestCase):
    def setUp(self):
        # Load the data to be unit tested
        self.df = pd.read_csv("premier_league_2023_2024_stats.csv")

    # Asserts that every value in the "team name" column is unique
    def test_team_name_unique(self):
        duplicates = self.df[self.df['team name'].duplicated()]['team name']
        self.assertTrue(
            duplicates.empty,
            f"Test failed: Not every value in the 'team name' column is unique. Duplicates found: {duplicates.tolist()}"
        )

    # Asserts that every value in the "team name" column is not null
    def test_team_name_not_null(self):
        null_values = self.df[self.df['team name'].isnull()]['team name']
        self.assertTrue(
            null_values.empty,
            f"Test failed: There are null values in the 'team name' column. Null values found: {null_values.tolist()}"
        )

    # Asserts that every value in the "team name" column exists in a predefined list
    def test_team_name_accepted_values(self):
        valid_team_names = {
            "Arsenal FC", "Aston Villa FC", "AFC Bournemouth", "Brentford FC", "Brighton & Hove Albion FC",
            "Burnley FC", "Chelsea FC", "Crystal Palace FC", "Everton FC", "Fulham FC", "Liverpool FC",
            "Luton Town FC", "Manchester City FC", "Manchester United FC", "Newcastle United FC",
            "Nottingham Forest FC", "Sheffield United FC", "Tottenham Hotspur FC", "West Ham United FC",
            "Wolverhampton Wanderers FC"
        }
        invalid_teams = self.df["team name"][~self.df["team name"].isin(valid_team_names)]
        self.assertTrue(
            invalid_teams.empty,
            f"Test failed: Invalid team names found. Invalid values: {invalid_teams.tolist()}"
        )

    # Asserts that the sum of 'won', 'drawn', and 'lost' columns is equal to or smaller than 38 for each team
    def test_total_matches_per_team(self):
        match_counts = self.df["won"] + self.df["drawn"] + self.df["lost"]
        invalid_rows = self.df[match_counts > 38]
        self.assertTrue(
            invalid_rows.empty,
            f"Test failed: Teams with more than 38 matches: {invalid_rows[['team name']].values.tolist()}"
        )

    # Asserts that the values in 'won', 'drawn', 'lost', 'goals for', and 'goals against' columns are non-negative
    def test_no_negative_values_in_stats(self):
        invalid_rows = self.df[
            (self.df["won"] < 0) | 
            (self.df["drawn"] < 0) | 
            (self.df["lost"] < 0) | 
            (self.df["goals for"] < 0) | 
            (self.df["goals against"] < 0)
        ]
        self.assertTrue(
            invalid_rows.empty,
            f"Test failed: Negative values found in the following rows: {invalid_rows[['team name']].values.tolist()}"
        )

if __name__ == '__main__':
    unittest.main()
