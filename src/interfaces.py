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
	def process(self, data: List[Dict[str, Any]]) -> IDataProcessor:
		"""
		Process the input data.
		
		Args:
			data: List of data dictionaries to process
			
		Returns:
			Self reference for method chaining
		"""
		pass
		
	@abstractmethod
	def save_to_csv(self, output_path: Optional[str] = None) -> None:
		"""
		Save processed data to CSV file.
		
		Args:
			output_path: Optional path where to save the CSV
			
		Returns:
			Self reference for method chaining
		"""
		pass