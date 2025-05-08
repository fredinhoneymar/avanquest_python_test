#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# apiconnector.py
# This module provides a connector to the football data API.
# It handles the REST API requests and responses, and provides methods to interact with the API.

from __future__ import annotations
import requests
import json
import time
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlencode
from typing import Dict, Any, Optional, Union, List

from interfaces import IConfigProvider, IConnector

class APIConnector(IConnector):
	"""
	Connector for the football data API.
	Follows REST conventions, so it can easily be reused for other APIs.
	Also supports caching for optimization and retry logic for failed requests.
	"""
	_instance = None
	
	def __new__(cls, config: Optional[IConfigProvider] = None):
		"""Ensure only one instance of APIConnector exists."""
		if cls._instance is None:
			if config is None:
				raise ValueError("Configuration must be provided for initial instantiation")
			cls._instance = super(APIConnector, cls).__new__(cls)
			cls._instance._initialized = False
		return cls._instance
	
	def __init__(self, config: Optional[IConfigProvider] = None):
		"""Initialize the API connector with the given configuration."""
		# Skip initialization if already done
		if hasattr(self, '_initialized') and self._initialized:
			return
		
		self.config = config
		self.logger = config.get_logger()
		
		# Core API properties
		self.base_url = config.get_config('url')
		self.api_key = config.get_config('token')
		self.timeout = config.get_config('timeout')
		self.max_retries = config.get_config('retry_attempts')		
		
		# Request configuration
		self.headers = {
			'X-Auth-Token': self.api_key,
			'Content-Type': 'application/json'
		}
		
		# Cache management
		self._enable_caching = config.get_config('enable_caching')
		self._cache_dir = config.get_config('cache_dir')
		self._cache_ttl = config.get_config('cache_ttl')
		self._cache = {}

		# Load cache and clear expired entries
		if self._enable_caching:
			self._clear_expired_cache()
			self._load_cache_from_files()
		
		# Current endpoint
		self._current_endpoint = None
		
		self._isSuccess = False
		self._initialized = True
		self.logger.debug("APIConnector initialized")

	def _clear_expired_cache(self) -> None:
		"""
		Clear expired cache entries based on cache_ttl from configuration.
		This is automatically called during initialization.
		"""
		if not self._enable_caching or not self._cache_dir or not hasattr(self, '_cache_ttl'):
			return
			
		try:
			# Create the cache directory if it doesn't exist
			if not self._cache_dir.exists():
				self._cache_dir.mkdir(parents=True, exist_ok=True)
				self.logger.debug(f"Created cache directory: {self._cache_dir}")
				return  # No files to clean if directory was just created
				
			# Get current time
			current_time = time.time()
			cleared_count = 0
			total_count = 0
			
			# Check each cache file
			for cache_file in self._cache_dir.glob('*.json'):
				total_count += 1
				try:
					# Read file metadata
					with open(cache_file, 'r') as f:
						cache_data = json.load(f)
					
					# Check if cache has expired
					file_timestamp = cache_data.get('timestamp', 0)
					age = current_time - file_timestamp
					
					if age > self._cache_ttl:
						# Delete expired file
						cache_file.unlink()
						cleared_count += 1
						self.logger.debug(f"Deleted expired cache file: {cache_file} (age: {int(age)} seconds)")
				except Exception as e:
					# If file is corrupted or can't be read, delete it
					self.logger.warning(f"Error processing cache file {cache_file}: {e}. File will be deleted.")
					try:
						cache_file.unlink()
						cleared_count += 1
					except Exception:
						pass
						
			if total_count > 0:
				self.logger.debug(f"Cache cleanup: {cleared_count} expired file(s) removed out of {total_count} total file(s) (TTL: {self._cache_ttl}s)")
		except Exception as e:
			self.logger.warning(f"Error during cache cleanup: {e}")

	def _get_cache_filename(self, cache_key: str) -> Path:
		"""Get a filename for a cache entry"""
		# Use an MD5 hash of the cache key as filename
		filename = hashlib.md5(cache_key.encode('utf-8')).hexdigest() + '.json'
		return self._cache_dir / filename

	def _save_cache_to_file(self, cache_key: str, data: Dict[str, Any]) -> None:
		"""Save a cache entry to a file"""
		if not self._enable_caching:
			return
			
		try:
			cache_file = self._get_cache_filename(cache_key)
			with open(cache_file, 'w') as f:
				json.dump({
					'timestamp': time.time(),
					'cache_key': cache_key,  		# Store the full cache key
					'url': cache_key.split(':')[1],	# Extract URL for debugging
					'data': data
				}, f, indent=2)
			self.logger.debug(f"Saved cache to file: {cache_file}")
		except Exception as e:
			self.logger.warning(f"Failed to write cache file: {e}")

	def _load_cache_from_files(self) -> None:
		"""Load all cached responses from files"""
		if not self._enable_caching:
			return
			
		try:
			# Create the cache directory if it doesn't exist
			self._cache_dir.mkdir(parents=True, exist_ok=True)
		except Exception as e:
			self.logger.warning(f"Failed to create cache directory {self._cache_dir}: {e}")
			return
			
		if not self._cache_dir.exists():
			self.logger.debug(f"Cache directory {self._cache_dir} does not exist")
			return
			
		count = 0
		for cache_file in self._cache_dir.glob('*.json'):
			try:
				with open(cache_file, 'r') as f:
					cache_data = json.load(f)
					
				# Use the stored cache key if available
				if 'cache_key' in cache_data:
					cache_key = cache_data['cache_key']
					self._cache[cache_key] = cache_data['data']
					count += 1
				# Fall back to reconstructing cache key
				elif 'url' in cache_data:
					url = cache_data.get('url', '')
					if url:
						cache_key = f"GET:{url}:{{}}:{{}}"
						self._cache[cache_key] = cache_data['data']
						count += 1
			except Exception as e:
				self.logger.warning(f"Error loading cache file {cache_file}: {e}")
		
		self.logger.debug(f"Loaded {count} cached responses from disk")

	def set_endpoint(self, endpoint: Union[str, Dict[str, Any]]) -> IConnector:
		"""
		Set the current endpoint for API requests.
		
		Args:
			endpoint: Either a string path ('/competitions/CL/matches')
					or a dictionary with path and parameters
		
		Returns:
			The APIConnector instance for method chaining
		"""
		if isinstance(endpoint, str):
			self._current_endpoint = {'path': endpoint}
		else:
			self._current_endpoint = endpoint
			
		self.logger.debug(f"Endpoint set to {self._current_endpoint}")
		return self

	def fetch(self, 
			endpoint: Optional[Union[str, Dict[str, Any]]] = None, 
			method: str = 'GET',
			params: Optional[Dict[str, Any]] = None,
			body: Optional[Dict[str, Any]] = None
		) -> Dict[str, Any]:
		"""
		Fetch data with the specified endpoint and method,
		following REST API conventions.
		
		Args:
			endpoint: Optional endpoint override
			method: HTTP method (GET, POST, etc.)
			params: Query parameters
			body: Request body for POST/PUT requests
			
		Returns:
			API response as dictionary
		"""
		# Use provided endpoint or the one set previously
		working_endpoint = endpoint if endpoint else self._current_endpoint
		if not working_endpoint:
			raise ValueError("No endpoint specified. Call set_endpoint() first or provide endpoint parameter.")
		
		# Build request parameters
		path = working_endpoint.get('path', '')
		path = path.lstrip('/') if isinstance(path, str) else path
		params = params or working_endpoint.get('params', {})
		
		# Build URL and add query parameters if needed
		url = urljoin(self.base_url, path)
		
		# Check cache before making request
		cache_key = f"{method}:{url}:{json.dumps(params or {}, sort_keys=True)}:{json.dumps(body or {}, sort_keys=True)}"
		if self._enable_caching and method == 'GET' and cache_key in self._cache:
			self.logger.info(f"Using cached response for {url}?{urlencode(params or {})}")
			setattr(self, '_isSuccess', True)
			return self._isSuccess, self._cache[cache_key]
		elif self._enable_caching and method == 'GET':
			self.logger.debug(f"No cached data for {url}")
		
		# If no cache, then make request with retry logic
		retries = 0
		self.logger.info(f"Making request {method}{url}?{urlencode(params or {})}")
		while retries <= self.max_retries:
			try:
				if method == 'GET':
					response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
				elif method == 'POST':
					response = requests.post(url, headers=self.headers, params=params, 
											json=body, timeout=self.timeout)
				elif method == 'PUT':
					response = requests.put(url, headers=self.headers, params=params, 
											json=body, timeout=self.timeout)
				else:
					raise ValueError(f"Unsupported HTTP method: {method}")
				
				# Handle HTTP error status codes
				response.raise_for_status()
				
				# Parse and cache response
				data = response.json()
				if self._enable_caching and method == 'GET':
					self.logger.debug(f"Storing response in cache for {url}")
					self._cache[cache_key] = data
					self._save_cache_to_file(cache_key, data)
				
				# If the request was successful
				setattr(self, '_isSuccess', True)
					
				# Log successful response
				self.logger.info(f"Data fetched with status code {response.status_code} for {params}")

				return self._isSuccess, data
				
			except requests.exceptions.HTTPError as e:
				if retries >= self.max_retries:
					self.logger.error(f"HTTP error after {retries} retries: {e}")
					raise
					
				# Handle rate limiting
				# See: https://docs.football-data.org/general/v4/policies.html#_request_throttling
				if response.status_code == 429:
					wait_time = int(response.headers.get('Retry-After', retries * 2 + 1))
					self.logger.warning(f"Rate limited. Waiting {wait_time} seconds")
					time.sleep(wait_time)
				elif response.status_code == 403:
					self.logger.debug(f"""Access denied: 
					{e}, 
					This endpoint may require a paid subscription tier at football-data.org"""
					)
					setattr(self, '_isSuccess', False)
					raise
				else:
					wait_time = (2 ** retries) + 1
					self.logger.warning(f"Request failed with {e}, retrying in {wait_time}s")
					time.sleep(wait_time)
					
			except requests.exceptions.RequestException as e:
				if retries >= self.max_retries:
					self.logger.error(f"Request error after {retries} retries: {e}")
					raise
				wait_time = (2 ** retries) + 1
				self.logger.warning(f"Request error: {e}, retrying in {wait_time}s")
				time.sleep(wait_time)
				
			retries += 1
			
	def clear_cache(self) -> None:
		"""Clear the response cache."""
		self._cache = {}
		self.logger.debug("Request cache cleared")
		
	def enable_caching(self, enable: bool) -> None:
		"""Enable or disable caching at runtime if needed."""
		self._enable_caching = enable
		self.logger.debug(f"Caching {'enabled' if enable else 'disabled'}")
