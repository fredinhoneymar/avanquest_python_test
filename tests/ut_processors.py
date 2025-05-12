#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ut_processors.py
# Unit tests for the data processors

import pytest
import csv
from unittest.mock import Mock, patch
from pathlib import Path
from typing import Optional, List, Dict, Any

from src.processors import BaseDataProcessor, PremierLeagueDataProcessor
from src.reporter import DataQualityChecker
from tests.mockconfigprovider import MockConfigProvider, temp_cache_dir, temp_output_dir, mock_config


@pytest.fixture
def mock_quality_checker() -> Mock:
	"""Create a mock quality checker."""
	mock = Mock(spec=DataQualityChecker)
	mock.check_data_quality.return_value = {
		'summary': {'quality_score': 0.95},
		'issues': []
	}
	mock.save_report.return_value = None
	return mock

@pytest.fixture
def premier_league_processor(mock_config) -> PremierLeagueDataProcessor:
	"""Create a PremierLeagueDataProcessor instance for testing."""
	return PremierLeagueDataProcessor(mock_config)

@pytest.fixture
def sample_standings_data() -> List[Dict[str, Any]]:
	"""Sample data for testing the processor."""
	return [{
		'filters': {'season': '2021'},
		'competition': {'name': 'Premier League'},
		'standings': [
			{
				'stage': 'REGULAR_SEASON',
				'type': 'TOTAL',
				'table': [
					{
						'position': 1,
						'team': {'id': 1, 'name': 'Manchester City', 'shortName': 'Man City'},
						'playedGames': 38,
						'won': 29,
						'draw': 6,
						'lost': 3,
						'points': 93,
						'goalsFor': 99,
						'goalsAgainst': 26,
						'goalDifference': 73
					},
					{
						'position': 2,
						'team': {'id': 2, 'name': 'Liverpool', 'shortName': 'Liverpool'},
						'playedGames': 38,
						'won': 28,
						'draw': 8,
						'lost': 2,
						'points': 92,
						'goalsFor': 94,
						'goalsAgainst': 26,
						'goalDifference': 68
					}
				]
			}
		]
	}]


class TestBaseDataProcessor:

	def test_initialization(self, mock_config: MockConfigProvider) -> None:
		"""Test initialization with config."""
		processor = BaseDataProcessor(mock_config)
		assert processor.config is mock_config
		assert processor.logger is mock_config.get_logger()
		assert processor.output_dir == Path(mock_config.get_config('output_dir'))
		assert processor.processed_data == []
		assert processor._processing_success is False
		assert processor.quality_enabled is True
	
	def test_init_without_config(self) -> None:
		"""Test initialization without config should raise error."""
		with pytest.raises(ValueError, match="Configuration provider must be provided"):
			BaseDataProcessor(None)

	def test_add_data_lineage_empty_data(self, mock_config: MockConfigProvider) -> None:
		"""Test adding data lineage with no data."""
		processor = BaseDataProcessor(mock_config)
		processor._add_data_lineage()
		mock_config.get_logger().warning.assert_called_once()

	def test_add_data_lineage_disabled(self, mock_config: MockConfigProvider) -> None:
		"""Test adding data lineage when disabled in config."""
		mock_config.config['add_data_lineage'] = False
		processor = BaseDataProcessor(mock_config)
		processor.processed_data = [{'name': 'test'}]
		
		processor._add_data_lineage()

		assert 'ProcessedAt' not in processor.processed_data[0]
		assert 'DataSource' not in processor.processed_data[0]

	def test_add_data_lineage(self, mock_config: MockConfigProvider) -> None:
		"""Test adding data lineage when enabled."""
		mock_config.config['add_data_lineage'] = True
		processor = BaseDataProcessor(mock_config)
		processor.processed_data = [{'name': 'test'}]
		processor.csv_headers = ['name']

		processor._add_data_lineage(source="Test Source")
		
		assert 'ProcessedAt' in processor.processed_data[0]
		assert 'DataSource' in processor.processed_data[0]
		assert processor.processed_data[0]['DataSource'] == "Test Source"
		assert 'ProcessedAt' in processor.csv_headers
		assert 'DataSource' in processor.csv_headers

	def test_check_data_quality_disabled(self, mock_config: MockConfigProvider) -> None:
		"""Test checking data quality when disabled."""
		mock_config.config['data_quality_report'] = False
		processor = BaseDataProcessor(mock_config)
		result = processor.check_data_quality()
		assert result is processor  # Returns self for chaining
		assert not hasattr(processor, 'quality_report')

	def test_check_data_quality_no_data(self, mock_config: MockConfigProvider) -> None:
		"""Test checking data quality with no processed data."""
		processor = BaseDataProcessor(mock_config)
		result = processor.check_data_quality()
		assert result is processor  # Returns self for chaining
		mock_config.get_logger().warning.assert_called_once()
	
	@patch('src.processors.DataQualityChecker')
	def test_check_data_quality(self, MockChecker: Mock, mock_config: MockConfigProvider) -> None:
		"""Test checking data quality with processed data."""
		# Setup mock quality checker with proper object structure
		mock_checker = Mock()
		
		# Create a mock report object
		mock_report = Mock()
		mock_report.summary = {'quality_score': 0.95}
		mock_report.issues = []
		mock_report.get_issue_count_by_severity = Mock(return_value={'ERROR': 0, 'WARNING': 0})
		
		mock_checker.check_data_quality.return_value = mock_report
		MockChecker.return_value = mock_checker
		
		processor = BaseDataProcessor(mock_config)
		processor.processed_data = [{'name': 'test'}]
		processor.csv_headers = ['name']
		
		result = processor.check_data_quality()
		
		assert result is processor  # Returns self for chaining
		assert processor.quality_report == mock_report
		mock_checker.check_data_quality.assert_called_once_with(
			processor.processed_data, processor.csv_headers)
		mock_checker.save_report.assert_called_once()
	
	def test_get_quality_score_no_report(self, mock_config: MockConfigProvider) -> None:
		"""Test getting quality score with no report."""
		processor = BaseDataProcessor(mock_config)
		assert processor.get_quality_score() == 0.0

	def test_get_quality_score(self, mock_config: MockConfigProvider) -> None:
		"""Test getting quality score with a report."""
		processor = BaseDataProcessor(mock_config)
		# Create a mock report object with a summary
		mock_report = Mock()
		mock_report.summary = {'quality_score': 0.95}
		processor.quality_report = mock_report

		assert processor.get_quality_score() == 0.95

	def test_process_not_implemented(self, mock_config: MockConfigProvider) -> None:
		"""Test that process() raises NotImplementedError."""
		processor = BaseDataProcessor(mock_config)
		with pytest.raises(NotImplementedError):
			processor.process([])

	def test_save_to_csv_no_data(self, mock_config: MockConfigProvider) -> None:
		"""Test saving to CSV with no data."""
		processor = BaseDataProcessor(mock_config)
		result = processor.save_to_csv()
		assert result is processor  # Returns self for chaining
		mock_config.get_logger().error.assert_called_once()

	def test_save_to_csv(self, mock_config: MockConfigProvider, temp_output_dir: Path) -> None:
		"""Test saving data to CSV."""
		processor = BaseDataProcessor(mock_config)
		processor.processed_data = [
			{'name': 'Team A', 'points': 10},
			{'name': 'Team B', 'points': 8}
		]
		processor.csv_headers = ['name', 'points']
		
		# Test with default path
		result = processor.save_to_csv()
		assert result is processor  # Returns self for chaining
		
		# Check that a file was created
		csv_files = list(temp_output_dir.glob('*.csv'))
		assert len(csv_files) == 1
		
		# Verify file contents
		with open(csv_files[0], 'r', newline='', encoding='utf-8') as f:
			reader = csv.DictReader(f)
			rows = list(reader)
			assert len(rows) == 2
			assert rows[0]['name'] == 'Team A'
			assert rows[0]['points'] == '10'
			assert rows[1]['name'] == 'Team B'
			assert rows[1]['points'] == '8'

	def test_save_to_csv_custom_path(self, mock_config: MockConfigProvider, temp_output_dir: Path) -> None:
		"""Test saving data to CSV with a custom path."""
		processor = BaseDataProcessor(mock_config)
		processor.processed_data = [{'name': 'test'}]
		processor.csv_headers = ['name']
		
		custom_path = str(temp_output_dir / 'custom.csv')
		result = processor.save_to_csv(custom_path)
		
		assert result is processor  # Returns self for chaining
		assert Path(custom_path).exists()


class TestPremierLeagueDataProcessor:
	
	def test_initialization(self, mock_config: MockConfigProvider) -> None:
		"""Test initialization with config."""
		processor = PremierLeagueDataProcessor(mock_config)
		assert processor.config is mock_config
		assert processor.csv_headers == [
			'Season', 'Stage', 'TeamName', 'Won', 'Draw',
			'Lost', 'GoalsFor', 'GoalsAgainst'
		]

	def test_process_empty_data(self, premier_league_processor: PremierLeagueDataProcessor) -> None:
		"""Test processing with no data."""
		result = premier_league_processor.process([])
		assert result is premier_league_processor  # Returns self for chaining
		assert premier_league_processor._processing_success is False
		premier_league_processor.logger.error.assert_called_once()

	def test_process_valid_data(self, premier_league_processor: PremierLeagueDataProcessor, sample_standings_data: List[dict]) -> None:
		"""Test processing with valid data."""
		result = premier_league_processor.process(sample_standings_data)
		
		assert result is premier_league_processor  # Returns self for chaining
		assert premier_league_processor._processing_success is True
		assert len(premier_league_processor.processed_data) == 2  # Two teams
		
		# Verify processed data
		team1 = premier_league_processor.processed_data[0]
		assert team1['Season'] == '2021'
		assert team1['Stage'] == 'REGULAR_SEASON_TOTAL'
		assert team1['TeamName'] == 'Manchester City'
		assert team1['Won'] == 29
		assert team1['Draw'] == 6
		assert team1['Lost'] == 3
		assert team1['GoalsFor'] == 99
		assert team1['GoalsAgainst'] == 26
		
		# Verify data lineage was added
		assert 'ProcessedAt' in team1
		assert 'DataSource' in team1
		assert team1['DataSource'] == 'https://api.football-data.org/v4/'

	def test_process_invalid_data(self, premier_league_processor: PremierLeagueDataProcessor) -> None:
		"""Test processing with invalid data structure."""
		invalid_data = [{'not_valid': 'structure'}]
		
		result = premier_league_processor.process(invalid_data)
		
		assert result is premier_league_processor  # Returns self for chaining
		assert premier_league_processor._processing_success is False
		premier_league_processor.logger.error.assert_called()

	def test_process_multiple_data_sources(self, premier_league_processor: PremierLeagueDataProcessor) -> None:
		"""Test processing multiple data sources."""
		data1 = [{
			'filters': {'season': '2021'},
			'competition': {'name': 'Premier League'},
			'standings': [{
				'stage': 'REGULAR_SEASON',
				'type': 'TOTAL',
				'table': [{
					'team': {'name': 'Team A'},
					'won': 10, 'draw': 5, 'lost': 3,
					'goalsFor': 30, 'goalsAgainst': 15
				}]
			}]
		}]
		
		data2 = [{
			'filters': {'season': '2022'},
			'competition': {'name': 'Premier League'},
			'standings': [{
				'stage': 'REGULAR_SEASON',
				'type': 'TOTAL',
				'table': [{
					'team': {'name': 'Team B'},
					'won': 8, 'draw': 6, 'lost': 4,
					'goalsFor': 25, 'goalsAgainst': 20
				}]
			}]
		}]
		
		# Process first data source
		premier_league_processor.process(data1)
		assert len(premier_league_processor.processed_data) == 1
		
		# Process second data source
		result = premier_league_processor.process(data2)
		
		# Should overwrite the previous data, not append
		assert result is premier_league_processor
		assert premier_league_processor._processing_success is True
		assert len(premier_league_processor.processed_data) == 1
		assert premier_league_processor.processed_data[0]['Season'] == '2022'
