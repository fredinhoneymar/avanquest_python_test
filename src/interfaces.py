#!/usr/bin/env python
# -*- coding: utf-8 -*-

# interfaces.py
# This module defines interfaces for the application components.

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Union, Any, Optional


class IConfigProvider(ABC):
	"""Interface for configuration providers."""
	
	@abstractmethod
	def get_logger(self) -> Any:
		"""Get the logger instance."""
		pass

	@abstractmethod
	def get_config(self, key: str, default: Any = None) -> Any:
		"""Get a configuration value."""
		pass

	@abstractmethod
	def set_config(self, key: str, value: Any) -> None:
		"""Set a configuration value."""
		pass


class IConnector(ABC):
	"""Interface for RESTful API connectors."""
	
	@abstractmethod
	def set_endpoint(self, endpoint: str) -> IConnector:
		"""Set the API endpoint."""
		pass

	@abstractmethod
	def fetch(	self, 
				endpoint: Optional[Union[str, Dict[str, Any]]] = None, 
				method: str = 'GET',
				params: Optional[Dict[str, Any]] = None,
				body: Optional[Dict[str, Any]] = None
			) -> Tuple[bool, Dict[str, Any]]:
		"""Fetch data from the API."""
		pass

	@abstractmethod
	def enable_caching(self, enable: bool) -> None:
		"""Enable or disable caching."""
		pass


class IDataProcessor(ABC):
	"""Interface for data processors that transform API data to other formats."""
	
	@abstractmethod
	def process(self, data_list: List[Dict[str, Any]]) -> IDataProcessor:
		"""Process the input data."""
		pass
		
	@abstractmethod
	def save_to_csv(self, output_path: Optional[str] = None) -> IDataProcessor:
		"""Save processed data to CSV file."""
		pass
	
	@abstractmethod
	def check_data_quality(self) -> IDataProcessor:
		"""Run data quality checks on the processed data."""
		pass
	
class IDataQualityChecker(ABC):
	"""Interface for data quality checkers."""
	
	@abstractmethod
	def check_data_quality(self, data: List[Dict[str, Any]], expected_columns: List[str] = None) -> Dict[str, Any]:
		"""Check the quality of processed data and generate a report."""
		pass
	
	@abstractmethod
	def save_report(self, prefix: str = "data_quality_report") -> None:
		"""Save the quality report to a file."""
		pass
