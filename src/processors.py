#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# football_data_processor.py
# This module processes football statistics data and exports to CSV

from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Type, Optional

from interfaces import IConfigProvider, IDataProcessor
from reporter import DataQualityChecker


class BaseDataProcessor(IDataProcessor):
	"""
	Base class for data processors that provides common functionality.
	"""
	
	def __init__(self, config: Optional[IConfigProvider] = None):
		"""Initialize the base data processor."""
		if config is None:
			raise ValueError('Configuration provider must be provided')
		self.config = config
		self.logger = config.get_logger()
		self.output_dir = Path(config.get_config('output_dir'))
		self.processed_data = []
		self._processing_success = False

		# Create quality checker if enabled in config
		self.quality_enabled = config.get_config('data_quality_report', False)
		if self.quality_enabled:
			self.quality_checker = DataQualityChecker(config)
			self.quality_report = None

	def _add_data_lineage(self, source: str = None) -> None:
		"""
		Add data lineage information to each record in the processed data.
		
		Args:
			source: Source identifier (e.g., 'Premier League API')
		"""
		if source is None:
			source = "Unknown Source"

		if not self.processed_data:
			self.logger.warning("No data to add lineage to. Call process() first.")
			return None

		# Check if data lineage is enabled in config
		if not self.config.get_config('add_data_lineage', False):
			return None
	
		# Current timestamp
		timestamp = datetime.now().isoformat()
		
		# Add lineage fields to each record
		for record in self.processed_data:
			record["ProcessedAt"] = timestamp
			record["DataSource"] = source
		
		# Update CSV headers to include lineage fields
		if hasattr(self, 'csv_headers') and self.csv_headers:
			# Add lineage fields if not already present
			lineage_fields = ["ProcessedAt", "DataSource"]
			for field in lineage_fields:
				if field not in self.csv_headers:
					self.csv_headers.append(field)
		
		self.logger.info(f"Added data lineage information")
		return None

	def check_data_quality(self) -> IDataProcessor:
		"""
		Run data quality checks on the processed data.
		
		Returns:
			Self reference for method chaining
		"""
		if not self.quality_enabled:
			return self
			
		if not self.processed_data:
			self.logger.warning('No data to check quality. Call process() first.')
			return self
		
		# Run quality checks
		expected_columns = getattr(self, 'csv_headers', None)
		self.quality_report = self.quality_checker.check_data_quality(
			self.processed_data, 
			expected_columns
		)
		
		# Save the report
		self.quality_checker.save_report()
			
		# Log issues summary
		if self.quality_report:
			issue_counts = self.quality_report.get_issue_count_by_severity()
			if issue_counts:
				self.logger.warning(f"Quality issues found: {issue_counts}")
				
		return self
	
	def get_quality_score(self) -> float:
		"""Get the data quality score (0.0-1.0) if quality checks were run."""
		if not hasattr(self, 'quality_report') or not self.quality_report:
			return 0.0
		return self.quality_report.summary.get('quality_score', 0.0)

	def process(self, data_list: List[Dict[str, Any]] = []) -> IDataProcessor:
		"""Process the input data."""
		raise NotImplementedError('Subclasses must implement process method')

	def save_to_csv(self, output_path: Optional[str] = None) -> IDataProcessor:
		"""Save the processed data to a CSV file."""
		
		# Check if processed data is available
		if not self.processed_data:
			self.logger.error('No data to save. Call process() first.')
			return self
		
		# Generate filename with timestamp
		if not output_path:
			timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
			filename = f"stats_{timestamp}.csv"
			output_path = str(self.output_dir / filename)
		
		# Check if the output directory exists, create if not
		if not self.output_dir.exists():
			self.output_dir.mkdir(parents=True, exist_ok=True)

		try:
			# Context manager to handle file I/O operations
			with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames=self.csv_headers)
				writer.writeheader()
				
				# Write rows in batches instead of loading all in memory
				batch_size = 1000
				for i in range(0, len(self.processed_data), batch_size):
					batch = self.processed_data[i:i+batch_size]
					writer.writerows(batch)

		except Exception as e:
			self.logger.error(f"Error saving CSV file: {e}")
		
		self.logger.info(f"Data saved to: {output_path}")
		return self


class PremierLeagueDataProcessor(BaseDataProcessor):
	"""
	Processes Premier League standings data and extracts team statistics.
	Converts the data to CSV format for analysis.
	"""
	
	def __init__(self, config: IConfigProvider):
		"""
		Initialize the Premier League data processor.
		
		Args:
			config: Configuration provider with access to output directory
		"""
		super().__init__(config)
		self.csv_headers = [
			'Season', 'Stage', 'TeamName', 'Won', 'Draw',
			'Lost', 'GoalsFor', 'GoalsAgainst'
		]
	
	def process(self, data_list: List[Dict[str, Any]]) -> PremierLeagueDataProcessor:
		"""
		Process Premier League data to extract team statistics.
		
		Args:
			data_list: List of API response data from successful API calls
			
		Returns:
			Self reference for method chaining
		"""
		if not data_list:
			self.logger.error('No data provided to process')
			self._processing_success = False
			return self
			
		self.processed_data = []
		processed_count = 0
		
		for response_data in data_list:
			try:
				# Get season year from filters section
				filters = response_data.get('filters', {})
				season_year = filters.get('season', '')
				
				# Process each standing group (e.g., REGULAR_SEASON, HOME, AWAY)
				standings = response_data.get('standings', [])
				if not standings:
					self.logger.warning(f"No standings data found in response for season {season_year}")
					continue
					
				for standing in standings:
					stage = standing.get('stage', '')
					stage_type = standing.get('type', 'TOTAL')
					combined_stage = f"{stage}_{stage_type}"
					
					# Process each team in the standings table
					for entry in standing.get('table', []):
						team_data = entry.get('team', {})
						team_name = team_data.get('name', '')
						
						# Extract required statistics
						team_stats = {
							'Season': season_year,
							'Stage': combined_stage,
							'TeamName': team_name,
							'Won': entry.get('won', 0),
							'Draw': entry.get('draw', 0),
							'Lost': entry.get('lost', 0),
							'GoalsFor': entry.get('goalsFor', 0),
							'GoalsAgainst': entry.get('goalsAgainst', 0)
						}
						self.processed_data.append(team_stats)
				
				processed_count += 1
				self.logger.info(f"Processed standings data for season {season_year}")
				
			except Exception as e:
				self.logger.error(f"Error processing data: {e}")
				continue
		
		if processed_count == 0:
			self.logger.error('No valid data could be processed')
			self._processing_success = False
			return self
		
		# Add data lineage if enabled in config
		api_source = self.config.get_config('url', None)
		self._add_data_lineage(source=api_source)

		self.logger.info(f"Successfully processed {len(self.processed_data)} team records from {processed_count} dataset(s)")
		self._processing_success = True
		return self
	