#!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# utils.py
# This module provides utility functions for the application.

import argparse
import traceback
from itertools import product
from typing import Dict, List, Any, Union, Optional, Tuple

from apiconnector import APIConnector

def create_arg_parser() -> argparse.ArgumentParser:
	"""
	Creates and returns an argument parser for command line arguments.
	
	Returns:
		argparse.ArgumentParser: Configured argument parser
	"""
	parser = argparse.ArgumentParser(description='Football Data API Client')
	parser.add_argument('endpoint', nargs='?', help='API endpoint (e.g., /competitions/PL/standings)')
	parser.add_argument('--params', nargs='+', help='API parameters as key=value pairs', default=[])
	parser.add_argument('--loglevel', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
						default='INFO', help='Set the logging level')
	parser.add_argument('--test', action='store_true', help='Test mode (no API calls)')
	return parser

def parse_params_to_dict(param_list: List[str]) -> Dict[str, str]:
	"""
	Helper function to convert a list of parameters in the format 'key=value' to a dictionary.
	
	Args:
		param_list: List of strings in 'key=value' format
		
	Returns:
		Dictionary with parsed parameters
	"""
	params_dict = {}
	for param in param_list:
		try:
			key, value = param.split('=', 1)
			params_dict[key] = value
		except ValueError as e:
			print(f"Error parsing parameter '{param}': {e}")
			traceback.print_exc()
	return params_dict

def parse_list_param(value: Any) -> Union[List[Union[int, str]], Any]:
	"""
	Helper function to parse a parameter value that might be in list format [val1,val2,...]
	
	Args:
		value: The value to parse, potentially in list format
		
	Returns:
		List of values if input was a list format string, otherwise the original value
	"""
	if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
		# Remove brackets and split by comma
		values = value[1:-1].split(',')
		# Convert numeric values to integers
		result = []
		for val in values:
			val = val.strip()
			if val.isdigit():
				result.append(int(val))
			else:
				result.append(val)
		return result
	return value

def process_multi_value_params(params: Dict[str, Any]) -> List[Dict[str, Any]]:
	"""
	Helper function to process parameters with multiple values and generate all combinations.
	
	Args:
		params: Dictionary of parameters where some values might be lists
		
	Returns:
		List of parameter dictionaries to use in separate API calls
	"""
	# Separate fixed and multi-value parameters
	fixed_params = {k: v for k, v in params.items() if not isinstance(v, list)}
	multi_params = {k: v for k, v in params.items() if isinstance(v, list)}
	
	# No multi-value params case
	if not multi_params:
		return [params]
	
	# Generate all combinations using itertools
	keys = multi_params.keys()
	values = multi_params.values()
	combinations = product(*values)
	
	# Merge with fixed parameters
	result = []
	for combo in combinations:
		param_dict = fixed_params.copy()
		param_dict.update(dict(zip(keys, combo)))
		result.append(param_dict)
		
	return result

def make_api_call(api_connector: APIConnector, 
				  endpoint: str, 
				  param_dict: Dict[str, Any], 
				  logger: Any
				) -> Tuple[Dict[str, Any], bool, Dict[str, Any]]:
	"""
	Helper function to make a single API call.
	This function is designed to be used with ThreadPoolExecutor.
	
	Args:
		api_connector: Initialized API connector instance
		endpoint: API endpoint to call
		param_dict: Parameter dictionary for this call
		logger: Logger instance
		
	Returns:
		Tuple of (param_dict, success_flag, response_data)
	"""
	try:
		# Convert param_dict to string for logging
		param_str = ", ".join(f"{k}={v}" for k, v in param_dict.items())
		logger.debug(f"Making API call to {endpoint} with params: {param_str}")
		
		# Make the API call
		isSuccess, data = api_connector.set_endpoint(endpoint).fetch(params=param_dict)
		
		if isSuccess:
			logger.debug(f"API call to {endpoint} with {param_str} succeeded")
			return (param_dict, True, data)
		else:
			error_message = data.get('message', 'Unknown error')
			logger.warning(f"API call to {endpoint} with {param_str} failed: {error_message}")
			return (param_dict, False, data)
			
	except Exception as e:
		logger.debug(traceback.format_exc())
		return (param_dict, False, {"error": str(e)})
