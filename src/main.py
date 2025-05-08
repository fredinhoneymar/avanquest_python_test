#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# main.py
# This script serves as the entry point for the application.

import sys
import argparse
import traceback
import json
import concurrent.futures
from itertools import product
from pathlib import Path
from typing import Dict, List, Any, Union, Optional, Tuple

from configuration import Configuration
from apiconnector import APIConnector
from processors import PremierLeagueDataProcessor

# Add the parent directory to the system path
if str(Path(__file__).resolve().parent) not in sys.path:
	sys.path.append(str(Path(__file__).resolve().parent))


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
		logger.error(f"Exception during API call to {endpoint}: {str(e)}")
		logger.debug(traceback.format_exc())
		return (param_dict, False, {"error": str(e)})


def main(endpoint: str, loglevel: str, **params ) -> int:
	"""
	Main function that orchestrates the data ingestion pipeline.
	
	Args:
		endpoint: API endpoint to call (e.g., '/competitions/PL/standings')
		loglevel: Logging level (DEBUG, INFO, WARNING, ERROR)
		**params: Optional parameters to pass to the API
	
	Returns:
		int: Return code (0 for success, 1 for failure)
	"""
	# Initialize the configuration
	config = Configuration(loglevel=loglevel)
		
	# Get the logger
	logger = config.get_logger()

	# Initialize the API connector with the configuration
	api_connector = APIConnector(config)
	
	# Parse any list parameters
	parsed_params = {}
	for key, value in params.items():
		parsed_params[key] = parse_list_param(value)
	
	# Process multi-value parameters to get all parameter combinations
	param_combinations = process_multi_value_params(parsed_params)
	
	if len(param_combinations) > 1:
		logger.info(f"Making {len(param_combinations)} API calls for different parameter combinations")
	
	# Store results from successful calls
	successful_results = []
	failed_params = []
	
	# Log the parameters being used for the API call
	logger.debug(f"Parameter combinations: {json.dumps(param_combinations, indent=2)}")

	# Make API calls for each parameter combination
	with concurrent.futures.ThreadPoolExecutor(max_workers=config.get_config('workers')) as executor:
		# Create a future for each parameter combination
		future_to_params = {
			executor.submit(make_api_call, api_connector, endpoint, param_dict, logger): param_dict
			for param_dict in param_combinations
		}
		
		# Process results as they complete
		for future in concurrent.futures.as_completed(future_to_params):
			param_dict, isSuccess, data = future.result()
			
			if isSuccess:
				successful_results.append(data)
			else:
				error_message = data.get('message', data.get('error', 'Unknown error'))
				failed_params.append((param_dict, error_message))
		
	if failed_params:
		logger.warning("Failed parameter combinations:")
		for params, error in failed_params:
			logger.warning(f"- {params}: {error}")
	
	# If none of the calls were successful, return error code
	if not successful_results:
		return 1

	# Process the data if it's Premier League standings
	if '/standings' in endpoint:
		processor = PremierLeagueDataProcessor(config)
		processor.process(successful_results).save_to_csv()
				

	# Return success code
	return 0


if __name__ == "__main__":
	# Create argument parser
	parser = argparse.ArgumentParser(description='Football Data API Client')
	parser.add_argument('endpoint', help='API endpoint (e.g., /competitions/PL/standings)')
	parser.add_argument('--params', '-p', nargs='+', help='API parameters as key=value pairs', default=[])
	parser.add_argument('--loglevel', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
						default='INFO', help='Set the logging level')
	
	# Parse arguments
	args = parser.parse_args()
		
	# Convert params list to dictionary
	params_dict = {}
	for param in args.params:
		try:
			key, value = param.split('=', 1)
			params_dict[key] = value
		except ValueError as e:
			print(f"Error parsing parameter '{param}': {e}")
			traceback.print_exc()
	
	# Call main function with parsed arguments
	try:
		ret = main(args.endpoint, loglevel=args.loglevel, **params_dict)
		sys.exit(ret)
	except Exception as e:
		print(f"Unhandled exception: {e}")
		traceback.print_exc()
		sys.exit(1)
		