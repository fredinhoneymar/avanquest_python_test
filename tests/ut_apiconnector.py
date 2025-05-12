#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ut_apiconnector.py
# Unit tests for the APIConnector class

import pytest
import json
import time
import sys
import shutil
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path
import requests
from typing import Optional, Generator

from src.apiconnector import APIConnector
from tests.mockconfigprovider import MockConfigProvider, temp_cache_dir, temp_output_dir, mock_config

@pytest.fixture
def test_specific_cache_dir() -> Generator[Path, None, None]:
	"""Create a specific temporary directory for cache-modifying tests only."""
	temp_dir = tempfile.mkdtemp()
	yield Path(temp_dir)
	# Cleanup after tests
	try:
		shutil.rmtree(temp_dir)
	except (FileNotFoundError, PermissionError):
		pass

@pytest.fixture
def test_specific_output_dir() -> Generator[Path, None, None]:
	"""Create a specific temporary directory for output files."""
	temp_dir = tempfile.mkdtemp()
	yield Path(temp_dir)
	# Cleanup after tests
	try:
		shutil.rmtree(temp_dir)
	except (FileNotFoundError, PermissionError):
		pass

@pytest.fixture
def api_connector(mock_config) -> Generator[APIConnector, None, None]:
	"""Create an APIConnector instance for testing."""
	# Reset singleton state for each test to ensure independence
	APIConnector._instance = None
	
	connector = APIConnector(mock_config)
	yield connector
	
	# Clean up temporary cache directory
	try:
		shutil.rmtree(mock_config.get_config('cache_dir'))
	except (FileNotFoundError, PermissionError):
		pass
	
	# Reset singleton state after test
	APIConnector._instance = None


class TestAPIConnector:

	def test_singleton_behavior(self, mock_config: MockConfigProvider) -> None:
		"""Test that APIConnector implements singleton pattern correctly."""
		# Reset singleton state to ensure test isolation
		APIConnector._instance = None
		
		# First initialization with config
		first_instance = APIConnector(mock_config)
		
		# Verify initial properties
		assert first_instance.config is mock_config
		assert first_instance.base_url == 'https://api.football-data.org/v4/'
		
		# Second initialization without config - should return same instance
		second_instance = APIConnector()
		
		# Verify instances are identical (same object)
		assert first_instance is second_instance
		assert id(first_instance) == id(second_instance)
		
		# Verify properties remained intact
		assert second_instance.config is mock_config
		assert second_instance.base_url == 'https://api.football-data.org/v4/'
		
		# Verify modifying one instance affects the other (because they're the same object)
		first_instance._current_endpoint = {'path': '/test/singleton'}
		assert second_instance._current_endpoint == {'path': '/test/singleton'}
		
		# Clean up
		APIConnector._instance = None

	def test_initialization(self, api_connector: APIConnector, mock_config: MockConfigProvider) -> None:
		"""Test connector initialization with config."""
		assert api_connector.config is mock_config
		assert api_connector.base_url == 'https://api.football-data.org/v4/'
		assert api_connector.api_key == 'test-api-token'
		assert api_connector.timeout == 10
		assert api_connector.max_retries == 2
		assert api_connector._enable_caching is True
		assert isinstance(api_connector._cache_dir, Path)
	
	def test_init_without_config(self) -> None:
		"""Test initialization without config should raise error."""
		# Reset singleton for this test
		APIConnector._instance = None
		
		with pytest.raises(ValueError, match='Configuration must be provided for initial instantiation'):
			APIConnector(None)

	def test_set_endpoint_string(self, api_connector: APIConnector) -> None:
		"""Test setting endpoint with string."""
		endpoint = '/competitions/PL/standings'
		result = api_connector.set_endpoint(endpoint)
		
		assert api_connector._current_endpoint == {'path': endpoint}
		assert result == api_connector  # Should return self for method chaining

	def test_set_endpoint_dict(self, api_connector: APIConnector) -> None:
		"""Test setting endpoint with dictionary."""
		endpoint = {'path': '/competitions/PL/standings', 'params': {'season': 2021}}
		result = api_connector.set_endpoint(endpoint)
		
		assert api_connector._current_endpoint == endpoint
		assert result == api_connector  # Should return self for method chaining

	def test_fetch_no_endpoint(self, api_connector: APIConnector) -> None:
		"""Test fetch without setting endpoint first"""
		with pytest.raises(ValueError, match='No endpoint specified'):
			api_connector.fetch()

	@patch('requests.get')
	def test_fetch_get_success(self, mock_get: Mock, api_connector: APIConnector) -> None:
		"""Test successful GET request."""
		# Mock the response from requests.get
		mock_response = Mock()
		mock_response.status_code = 200
		mock_response.json.return_value = {'data': 'test data'}
		mock_get.return_value = mock_response
		
		# Set endpoint and make fetch
		api_connector.set_endpoint('/test/endpoint')
		success, result = api_connector.fetch(params={'param1': 'value1'})
		
		# Validate the request was made with expected parameters
		mock_get.assert_called_once()
		args, kwargs = mock_get.call_args
		assert kwargs['params'] == {'param1': 'value1'}
		assert kwargs['timeout'] == 10
		assert 'X-Auth-Token' in kwargs['headers']
		
		# Check the result
		assert success is True
		assert result == {'data': 'test data'}

	@patch('requests.get')
	def test_fetch_retry_logic(self, mock_get: Mock, api_connector: APIConnector) -> None:
		"""Test retry logic for failed requests."""
		# First mock: call fails with 500
		mock_error_response = Mock()
		mock_error_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
		mock_error_response.status_code = 500

		# Second mock: call succeeds with 200
		mock_success_response = Mock()
		mock_success_response.status_code = 200
		mock_success_response.json.return_value = {'data': 'retry success'}

		mock_get.side_effect = [mock_error_response, mock_success_response]

		# Set endpoint and fetch
		api_connector.set_endpoint('/test/retry')
		with patch('time.sleep') as mock_sleep:  # Mock sleep to speed up test
			success, result = api_connector.fetch()
		
		# Verify retry occurred
		assert mock_get.call_count == 2
		assert mock_sleep.called

		# Check the final result
		assert success is True
		assert result == {'data': 'retry success'}

	@patch('requests.get')
	def test_fetch_max_retries_exceed(self, mock_get: Mock, api_connector: APIConnector) -> None:
		"""Test when max retries are exceeded."""
		# All calls fail with 500
		mock_response = Mock()
		mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
		mock_response.status_code = 500
		
		mock_get.return_value = mock_response
		
		# Set endpoint
		api_connector.set_endpoint('/test/max-retries')
		
		# Should fail after max retries
		with patch('time.sleep') as mock_sleep:  # Mock sleep to speed up test
			with pytest.raises(requests.exceptions.HTTPError):
				api_connector.fetch()
		
		# Verify retry count (initial + 2 retries = 3 calls)
		assert mock_get.call_count == 3
		assert mock_sleep.call_count == 2
	
	@patch('requests.get')
	def test_access_forbidden(self, mock_get: Mock, api_connector: APIConnector) -> None:
		"""Test handling of 403 Forbidden with no retry."""
		# Mock: call fails with 403 error
		mock_error_response_403 = Mock()
		mock_error_response_403.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")
		mock_error_response_403.status_code = 403

		mock_get.return_value = mock_error_response_403

		# Test 403 error
		api_connector.set_endpoint('/test/forbidden')
		with patch('time.sleep') as mock_sleep_403:
			with pytest.raises(requests.exceptions.HTTPError):
				api_connector.fetch()
		
		# Verify no retry for 403
		assert mock_get.call_count == 1
		assert not mock_sleep_403.called

	@patch('requests.get')
	def test_rate_limit_handling(self, mock_get: Mock, api_connector: APIConnector) -> None:
		"""Test proper handling of 429 Too Many Requests with Retry-After header."""
		# Mock response with 429 status and Retry-After header
		mock_response_429 = Mock()
		mock_response_429.status_code = 429
		mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
		mock_response_429.headers = {'Retry-After': '5'}  # API specifies retry time
		
		# Success response for after waiting
		mock_success_response = Mock()
		mock_success_response.status_code = 200
		mock_success_response.json.return_value = {'data': 'rate_limit_success'}
		
		# First call gets rate-limited, second succeeds
		mock_get.side_effect = [mock_response_429, mock_success_response]
		
		# Test rate limiting with retry
		api_connector.set_endpoint('/test/rate-limit')
		with patch('time.sleep') as mock_sleep:
			success, result = api_connector.fetch()

		# Verify that exactly 2 calls were made (initial + retry after waiting)
		assert mock_get.call_count == 2
		# Verify the Retry-After header was respected
		mock_sleep.assert_called_once_with(5)
		# Verify the final result is the success response
		assert mock_success_response.json.called
		assert success is True
		assert result == {'data': 'rate_limit_success'}

	@patch('requests.get')
	def test_fetch_connection_error(self, mock_get: Mock, api_connector: APIConnector) -> None:
		"""Test handling of connection errors."""
		# Mock connection error
		mock_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")
		
		# Set endpoint
		api_connector.set_endpoint('/test/connection-error')
		
		# Should raise the connection error after retries
		with patch('time.sleep') as mock_sleep:
			with pytest.raises(requests.exceptions.ConnectionError):
				api_connector.fetch()
		
		# Verify retry attempts
		assert mock_get.call_count == api_connector.max_retries + 1
		assert mock_sleep.call_count == api_connector.max_retries

	@patch('requests.get')
	def test_fetch_timeout_error(self, mock_get: Mock, api_connector: APIConnector) -> None:
		"""Test handling of timeout errors."""
		# Mock timeout
		mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
		
		# Set endpoint
		api_connector.set_endpoint('/test/timeout')
		
		# Should raise the timeout error after retries
		with patch('time.sleep') as mock_sleep:
			with pytest.raises(requests.exceptions.Timeout):
				api_connector.fetch()

	@patch('requests.get')
	def test_json_decode_error(self, mock_get: Mock, api_connector: APIConnector) -> None:
		"""Test handling of JSON decode errors."""
		# Create response with invalid JSON
		mock_response = Mock()
		mock_response.status_code = 200
		mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
		mock_get.return_value = mock_response
		
		# Set endpoint and make fetch
		api_connector.set_endpoint('/test/invalid-json')
		success, result = api_connector.fetch()
		
		# Check result indicates failure
		assert success is False
		assert "JSON decode error" in str(result)

	def test_unsupported_http_method(self, api_connector: APIConnector) -> None:
		"""Test with unsupported HTTP method."""
		api_connector.set_endpoint('/test')
		with pytest.raises(ValueError, match="Unsupported HTTP method"):
			api_connector.fetch(method='DELETE')

	@patch('requests.get')
	def test_caching_flow(self, mock_get: Mock, api_connector: APIConnector, temp_cache_dir: Path) -> None:
		"""Test complete caching flow - store and retrieve"""
		# Set up test configuration with temp directory
		api_connector.config.config['cache_dir'] = temp_cache_dir
		api_connector._cache_dir = temp_cache_dir
		api_connector._enable_caching = True
		
		# Mock fetch to return data
		mock_response = Mock()
		mock_response.status_code = 200
		mock_response.json.return_value = {'testKey': 'testValue'}
		mock_get.return_value = mock_response
		
		# First call should go to API
		api_connector.set_endpoint('/test/cache')
		success1, result1 = api_connector.fetch()
		
		# Second call should use cache
		success2, result2 = api_connector.fetch()
		
		# Verify API was called once
		assert mock_get.call_count == 1
		
		# Verify both results are the same
		assert success1 is True and success2 is True
		assert result1 == result2 == {'testKey': 'testValue'}
		
		# Verify cache file was created
		cache_files = list(temp_cache_dir.glob('*.json'))
		assert len(cache_files) == 1

	def test_enable_disable_caching(self, api_connector: APIConnector) -> None:
		"""Test enabling/disabling caching at runtime."""
		# Start with caching enabled
		assert api_connector._enable_caching is True
		
		# Disable it
		api_connector.enable_caching(False)
		assert api_connector._enable_caching is False
		
		# Re-enable it
		api_connector.enable_caching(True)
		assert api_connector._enable_caching is True

	def test_load_cache_from_files(self, api_connector: APIConnector, temp_cache_dir: Path) -> None:
		"""Test loading cache from files with different formats."""
		# Set up test configuration with temp directory
		api_connector.config.config['cache_dir'] = temp_cache_dir
		api_connector._cache_dir = temp_cache_dir
		api_connector._enable_caching = True
		api_connector._cache = {}  # Clear the cache
		
		# Create two types of cache files:
		# 1. Valid cache_key
		cache_file1 = temp_cache_dir / "valid_cache.json"
		with open(cache_file1, 'w') as f:
			json.dump({
				'timestamp': time.time(),
				'cache_key': 'GET:https://api.example.com/test1:{}:{}',
				'url': 'https://api.example.com/test1',
				'data': {'source': 'valid_format', 'value': 1}
			}, f)

		# 2. Invalid cache file
		cache_file2 = temp_cache_dir / 'invalid_cache.json'
		with open(cache_file2, 'w') as f:
			f.write('This is not valid JSON')

		# Call the method
		api_connector._load_cache_from_files()
		
		# Check results
		assert len(api_connector._cache) == 1  # Should load only 1 valid cache file

		# Verify the valid format cache was loaded correctly
		key = 'GET:https://api.example.com/test1:{}:{}'
		assert key in api_connector._cache
		assert api_connector._cache[key]['source'] == 'valid_format'
		assert api_connector._cache[key]['value'] == 1

		# Test with disabled caching
		api_connector._enable_caching = False
		api_connector._cache = {}
		api_connector._load_cache_from_files()
		assert len(api_connector._cache) == 0  # Should not load any files

	def test_cache_ttl_expiration(self, api_connector: APIConnector, test_specific_cache_dir: Path) -> None:
		"""Test cache expiration based on TTL"""
		# Set up test configuration with temp directory and short TTL
		api_connector.config.config['cache_dir'] = test_specific_cache_dir
		api_connector._cache_dir = test_specific_cache_dir
		api_connector._cache_ttl = 1  # 1 second TTL
		
		# Create a fake cache file that's already expired
		cache_file = test_specific_cache_dir / 'expired.json'
		with open(cache_file, 'w') as f:
			json.dump({
				'timestamp': time.time() - 2,  # 2 seconds old
				'cache_key': 'test:key',
				'url': 'https://test.com',
				'data': {'expired': True}
			}, f)
		
		# Now clear expired cache
		api_connector._clear_expired_cache()
		
		# Verify the file is gone
		assert not cache_file.exists()
