#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mockconfigprovider.py
# Shared test fixtures and utilities for all test modules

import pytest
import tempfile
import shutil
from unittest.mock import Mock
from pathlib import Path
from typing import Optional, Generator


class MockConfigProvider:
	"""Mock implementation of IConfigProvider for testing."""

	def __init__(self, config_values: Optional[dict] = None):
		self.config = config_values or {}
		self.logger = Mock()
		self.logger.debug = Mock()
		self.logger.info = Mock()
		self.logger.warning = Mock()
		self.logger.error = Mock()
	
	def get_logger(self) -> Mock:
		"""Return a mock logger."""
		return self.logger

	def get_config(self, key: str, default: Optional[str] = None) -> Optional[str]:
		"""	Get a configuration value by key."""
		return self.config.get(key, default)

	def set_config(self, key: str, value: Optional[str] = None) -> None:
		"""	Set a configuration value by key."""
		self.config[key] = value

@pytest.fixture
def mock_config(temp_cache_dir: Path, temp_output_dir: Path) -> MockConfigProvider:
	"""Create a mock configuration for testing."""
	return MockConfigProvider({
		'url': 'https://api.football-data.org/v4/',
		'token': 'test-api-token',
		'timeout': 10,
		'retry_attempts': 2,
		'enable_caching': True,
		'cache_dir': temp_cache_dir,
		'cache_ttl': 3600,
		'output_dir': temp_output_dir,
		'data_quality_report': True,
		'add_data_lineage': True,
	})

@pytest.fixture
def temp_cache_dir() -> Generator[Path, None, None]:
	"""Create a temporary directory for cache testing."""
	temp_dir = tempfile.mkdtemp()
	yield Path(temp_dir)
	# Cleanup after tests with error handling
	try:
		shutil.rmtree(temp_dir)
	except (FileNotFoundError, PermissionError):
		pass  # Directory may already be deleted

@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
	"""Create a temporary directory for output testing."""
	temp_dir = tempfile.mkdtemp()
	yield Path(temp_dir)
	# Cleanup after tests with error handling
	try:
		shutil.rmtree(temp_dir)
	except (FileNotFoundError, PermissionError):
		pass  # Directory may already be deleted

