#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# reporter.py
# This module provides a data quality checker for processed data.

import json
import pandas as pd
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from interfaces import IConfigProvider


class DataQualityReport:
	"""
	Class representing a data quality report with issues and metrics.
	"""
	def __init__(self):
		self.issues = []
		self.metrics = {}
		self.summary = {}
		
	def add_issue(self, severity: str, issue_type: str, description: str, affected_records: List[int] = None):
		"""Add an issue to the report."""
		self.issues.append({
			'severity': severity,
			'type': issue_type,
			'description': description,
			'affected_records': affected_records or []
		})
		
	def add_metric(self, name: str, value: Any):
		"""Add a metric to the report."""
		self.metrics[name] = value
		
	def set_summary(self, summary: Dict[str, Any]):
		"""Set the summary of the report."""
		self.summary = summary
		
	def get_issue_count_by_severity(self) -> Dict[str, int]:
		"""Get count of issues grouped by severity."""
		counts = defaultdict(int)
		for issue in self.issues:
			counts[issue['severity']] += 1
		return dict(counts)
	
	def to_dict(self) -> Dict[str, Any]:
		"""Convert report to dictionary."""
		return {
			'summary': self.summary,
			'metrics': self.metrics,
			'issues': self.issues,
			'issue_counts': self.get_issue_count_by_severity()
		}
	
	def to_json(self, indent: int = 2) -> str:
		"""Convert report to JSON string."""
		return json.dumps(self.to_dict(), indent=indent)
	
	def save(self, filepath: str):
		"""Save report to JSON file."""
		with open(filepath, 'w') as f:
			f.write(self.to_json())


class DataQualityChecker:
	"""
	Class for checking data quality of processed data.
	"""
	def __init__(self, config: IConfigProvider):
		self.config = config
		self.logger = config.get_logger()
		self.output_dir = Path(config.get_config('output_dir'))
		self.quality_report = None
		
	def check_data_quality(self, data: List[Dict[str, Any]], expected_columns: List[str] = None) -> DataQualityReport:
		"""
		Check the quality of processed data and generate a report.
		
		Args:
			data: List of dictionaries containing the processed data
			expected_columns: Expected columns in the data
			
		Returns:
			DataQualityReport object containing quality issues and metrics
		"""
		if not data:
			self.logger.warning('No data available for quality check')
			return None
		
		# Create a report instance
		self.quality_report = DataQualityReport()
		
		# Convert to DataFrame for easier analysis
		df = pd.DataFrame(data)
		
		# Run quality checks
		self._check_completeness(df, expected_columns)
		self._check_consistency(df)
		self._check_ranges(df)
		self._check_duplicates(df)
		self._check_missing_values(df)
		self._check_outliers(df)
		
		# Add basic metrics
		self._add_metrics(df)
		
		# Create summary
		quality_score = self._calculate_quality_score(df)
		self.quality_report.set_summary({
			'record_count': len(df),
			'column_count': len(df.columns),
			'issue_count': len(self.quality_report.issues),
			'quality_score': quality_score,
			'status': 'PASSED' if quality_score >= 0.8 else 'WARNING'
		})
		
		return self.quality_report
	
	def save_report(self, prefix: str = 'data_quality_report') -> None:
		"""
		Save the quality report to a file.
		
		Args:
			prefix: Prefix for the filename
		"""
		if not self.quality_report:
			self.logger.warning('No quality report to save')
			return

		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		filename = f"{prefix}_{timestamp}.json"
		
		if not self.output_dir.exists():
			self.output_dir.mkdir(parents=True, exist_ok=True)
			
		report_path = str(self.output_dir / filename)
		
		try:
			self.quality_report.save(report_path)
			self.logger.info(f"Data quality report saved to: {report_path}")
		except Exception as e:
			self.logger.error(f"Failed to save quality report: {e}")
			return

	def _calculate_quality_score(self, df: pd.DataFrame) -> float:
		"""Calculate an overall quality score based on issues."""
		if not self.quality_report:
			return 0.0
			
		# Count issues by severity
		issue_counts = self.quality_report.get_issue_count_by_severity()
		
		# Get total record count
		record_count = len(df) or 1
		
		# Calculate score based on issue severity
		error_weight = issue_counts.get('ERROR', 0) * 1.0
		warning_weight = issue_counts.get('WARNING', 0) * 0.5
		info_weight = issue_counts.get('INFO', 0) * 0.1
		
		total_weighted_issues = error_weight + warning_weight + info_weight
		
		# Score formula: 1 - (weighted issues / record count), minimum 0
		score = max(0, 1 - (total_weighted_issues / (record_count * 2)))
		return round(score, 2)
	
	def _check_completeness(self, df: pd.DataFrame, expected_columns: List[str] = None) -> None:
		"""Check if all required fields are present."""
		if not expected_columns:
			return
			
		missing_columns = set(expected_columns) - set(df.columns)
		if missing_columns:
			self.quality_report.add_issue(
				'ERROR',
				'MISSING_COLUMNS',
				f"Missing required columns: {', '.join(missing_columns)}"
			)
	
	def _check_consistency(self, df: pd.DataFrame) -> None:
		"""Check for data consistency."""
		# Example for football data: check if W+D+L = played games
		if all(col in df.columns for col in ["Won", "Draw", "Lost"]):
			# Calculate played games
			df['CalculatedPlayed'] = df['Won'] + df['Draw'] + df['Lost']
			
			# Check consistency if PlayedGames column exists
			if 'PlayedGames' in df.columns:
				inconsistent = df[df['CalculatedPlayed'] != df['PlayedGames']]
				if not inconsistent.empty:
					self.quality_report.add_issue(
						'ERROR',
						'INCONSISTENT_DATA',
						f"Inconsistent game counts: W+D+L != PlayedGames for {len(inconsistent)} records",
						inconsistent.index.tolist()
					)
					
	def _check_ranges(self, df: pd.DataFrame) -> None:
		"""Check if values are within expected ranges."""
		numeric_columns = df.select_dtypes(include='number').columns
		
		for col in numeric_columns:
			# Check for negative values that should be positive
			if col in ['Won', 'Draw', 'Lost', 'GoalsFor', 'GoalsAgainst']:
				negative_values = df[df[col] < 0]
				if not negative_values.empty:
					self.quality_report.add_issue(
						'ERROR',
						'NEGATIVE_VALUES',
						f"Negative values found in {col}: {len(negative_values)} records affected",
						negative_values.index.tolist()
					)
					
	def _check_duplicates(self, df: pd.DataFrame) -> None:
		"""Check for duplicate records."""
		# Define a subset of columns that should be unique together
		# For football standings, a team should appear once per season and stage
		if all(col in df.columns for col in ['Season', 'Stage', 'TeamName']):
			duplicate_keys = df.duplicated(subset=['Season', 'Stage', 'TeamName'], keep=False)
			duplicates = df[duplicate_keys]
			
			if not duplicates.empty:
				self.quality_report.add_issue(
					'WARNING',
					'DUPLICATE_RECORDS',
					f"Duplicate team entries found: {len(duplicates)} records",
					duplicates.index.tolist()
				)
				
	def _check_missing_values(self, df: pd.DataFrame) -> None:
		"""Check for missing values in important fields."""
		for col in df.columns:
			missing = df[df[col].isna()]
			if not missing.empty:
				self.quality_report.add_issue(
					'WARNING',
					'MISSING_VALUES',
					f"Missing values in {col}: {len(missing)} records affected",
					missing.index.tolist()
				)
				
	def _check_outliers(self, df: pd.DataFrame) -> None:
		"""Check for outlier values that might indicate errors."""
		numeric_columns = df.select_dtypes(include='number').columns
		
		for col in numeric_columns:
			# Skip columns where outliers might be legitimate
			if col not in ['Season']:
				# Use IQR method to detect outliers
				Q1 = df[col].quantile(0.25)
				Q3 = df[col].quantile(0.75)
				IQR = Q3 - Q1
				
				lower_bound = Q1 - 1.5 * IQR
				upper_bound = Q3 + 1.5 * IQR
				
				outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
				if not outliers.empty:
					self.quality_report.add_issue(
						'INFO',
						'POTENTIAL_OUTLIERS',
						f"Potential outliers in {col}: {len(outliers)} records affected",
						outliers.index.tolist()
					)
					
	def _add_metrics(self, df: pd.DataFrame) -> None:
		"""Add basic data quality metrics to the report."""
		# Column-level metrics
		for col in df.columns:
			if col in df.select_dtypes(include='number').columns:
				self.quality_report.add_metric(f"{col}_min", float(df[col].min()))
				self.quality_report.add_metric(f"{col}_max", float(df[col].max()))
				self.quality_report.add_metric(f"{col}_mean", round(float(df[col].mean()), 2))
				
		# Completeness metrics
		self.quality_report.add_metric('completeness', round(1 - df.isna().sum().sum() / (df.shape[0] * df.shape[1]), 4))
		
		# Uniqueness metrics
		if 'TeamName' in df.columns:
			self.quality_report.add_metric('unique_teams', int(df['TeamName'].nunique()))

		if 'Season' in df.columns:
			self.quality_report.add_metric('seasons_covered', int(df['Season'].nunique()))
