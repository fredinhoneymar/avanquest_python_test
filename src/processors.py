#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# football_data_processor.py
# This module processes football statistics data and exports to CSV

from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from interfaces import IConfigProvider, IDataProcessor


class PremierLeagueDataProcessor(IDataProcessor):
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
		self.config = config
		self.logger = config.get_logger()
		self.output_dir = Path(config.get_config('output_dir'))
		self.processed_data = []
		self.csv_headers = [
			"Season", "Stage", "TeamName", "Won", "Draw", 
			"Lost", "GoalsFor", "GoalsAgainst"
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
			self.logger.error("No data provided to process")
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
					
					# Process each team in the standings table
					for entry in standing.get('table', []):
						team_data = entry.get('team', {})
						team_name = team_data.get('name', '')
						
						# Extract required statistics
						team_stats = {
							"Season": season_year,
							"Stage": stage,
							"TeamName": team_name,
							"Won": entry.get('won', 0),
							"Draw": entry.get('draw', 0),
							"Lost": entry.get('lost', 0),
							"GoalsFor": entry.get('goalsFor', 0),
							"GoalsAgainst": entry.get('goalsAgainst', 0)
						}
						self.processed_data.append(team_stats)
				
				processed_count += 1
				self.logger.info(f"Processed standings data for season {season_year}")
				
			except Exception as e:
				self.logger.error(f"Error processing data: {e}")
				continue
		
		if processed_count == 0:
			self.logger.error("No valid data could be processed")
			self._processing_success = False
			return self
			
		self.logger.info(f"Successfully processed {len(self.processed_data)} team records from {processed_count} datasets")
		self._processing_success = True
		return self

	def save_to_csv(self, output_path: Optional[str] = None) -> None:
		"""
		Save the processed data to a CSV file.
		
		Args:
			output_path: Optional custom output path
			
		Returns:
			Self reference for method chaining
		"""
		if not self.processed_data:
			self.logger.error("No data to save. Call process() first.")
			return
		
		# Generate filename with timestamp
		if not output_path:
			timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
			filename = f"premier_league_stats_{timestamp}.csv"
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
