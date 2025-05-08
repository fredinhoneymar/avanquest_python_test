import pandas as pd
import os
from config.settings import OUTPUT_DIR
from config.logging_config import setup_logger

def initialize_team_stats(team_stats, team):
    """Ensures that the team has an initialized dictionary"""
    if team not in team_stats:
        team_stats[team] = {
            'wins': 0, 'draws': 0, 'losses': 0,
            'goals_for': 0, 'goals_against': 0
        }

def process_matches(matches, logger):
    """Processes the matches and calculates statistics for each team"""
    team_stats = {}

    for match in matches:
        if match['status'] != 'FINISHED':
            continue

        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        home_goals = match['score']['fullTime']['home']
        away_goals = match['score']['fullTime']['away']

        initialize_team_stats(team_stats, home)
        initialize_team_stats(team_stats, away)

        # Atualiza gols
        team_stats[home]['goals_for'] += home_goals
        team_stats[home]['goals_against'] += away_goals
        team_stats[away]['goals_for'] += away_goals
        team_stats[away]['goals_against'] += home_goals

        # Atualiza resultado
        if home_goals > away_goals:
            team_stats[home]['wins'] += 1
            team_stats[away]['losses'] += 1
        elif home_goals < away_goals:
            team_stats[away]['wins'] += 1
            team_stats[home]['losses'] += 1
        else:
            team_stats[home]['draws'] += 1
            team_stats[away]['draws'] += 1

    logger.info(f" Processed data: {len(team_stats)} times")
    return team_stats

def save_to_csv(data, season_year, logger):
    """Saves the statistics to a CSV file"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    df = pd.DataFrame.from_dict(data, orient='index').reset_index()
    df = df.rename(columns={'index': 'team'})
    filename = os.path.join(OUTPUT_DIR, f"epl_stats_{season_year}.csv")
    df.to_csv(filename, index=False, sep=';', encoding='utf-8')
    logger.info(f" File saved: {filename}")
