#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# main.py
# This script serves as the entry point for the application.
# It orchestrates the data ingestion pipeline by calling the API and processing the data.
# It also includes a test mode for running unit tests.

__author__ = 'Michael Garancher'
__email__ = 'michaelgarancher1@gmail.com'
__version__ = '1.0.0'

import sys
import traceback
from importlib.util import spec_from_file_location, module_from_spec
import concurrent.futures
from pathlib import Path

from configuration import Configuration
from apiconnector import APIConnector
from processors import PremierLeagueDataProcessor

from utils import (
	create_arg_parser, parse_params_to_dict, parse_list_param, 
	process_multi_value_params, make_api_call
)


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
	
	# Parse any list parameters to get all parameter combinations
	parsed_params = {}
	for key, value in params.items():
		parsed_params[key] = parse_list_param(value)

	param_combinations = process_multi_value_params(parsed_params)
	
	# Store results from successful calls
	successful_results = []
	failed_params = []

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
		logger.debug('Failed parameter combinations:')
		for params, error in failed_params:
			logger.debug(f"- {params}: {error}")

	# If none of the calls were successful, return error code
	if not successful_results:
		return 1

	# Process the data if it's the standings endpoint
	if '/standings' in endpoint:
		processor = PremierLeagueDataProcessor(config)
		processor.process(successful_results).save_to_csv()

		# Check data quality if enabled
		if hasattr(processor, 'quality_enabled') and processor.quality_enabled:
			processor.check_data_quality()

	# Return success code
	return 0

def run_tests() -> int:
	"""Run unit tests using the main_unittest.py orchestrator."""

	# Find the path to the test orchestrator
	src_dir = Path(__file__).resolve().parent
	project_dir = src_dir.parent
	test_dir = project_dir / 'tests'
	orchestrator_path = test_dir / 'main_unittest.py'

	if not orchestrator_path.exists():
		print(f"Error: Test orchestrator not found at {orchestrator_path}")
		return 1
	
	# Add the test directory to Python's path
	sys.path.insert(0, str(project_dir))
	sys.path.insert(0, str(test_dir))
	
	# Import the test orchestrator module
	try:
		spec = spec_from_file_location('main_unittest', orchestrator_path)
		main_unittest = module_from_spec(spec)
		spec.loader.exec_module(main_unittest)
		
		# Run all tests with default settings
		return main_unittest.main()
	except Exception as e:
		print(f"Error running tests: {e}")
		traceback.print_exc()
		return 1


if __name__ == "__main__":
	# Add the parent directory to the system path for proper module imports
	# This is necessary if the script is run directly from the src directory
	if str(Path(__file__).resolve().parent) not in sys.path:
		sys.path.append(str(Path(__file__).resolve().parent))

	# Create argument parser
	parser = create_arg_parser()
	
	# Parse arguments
	args = parser.parse_args()
		
	# Check if we're running in test mode
	if args.test:
		sys.exit(run_tests())
	# Else run normal operation
	else:
		# Check if an endpoint is provided
		if not args.endpoint:
			parser.error('Parameter required: endpoint')
			sys.exit(1)
			
		# Convert params list to dictionary
		params_dict = parse_params_to_dict(args.params)
		
		# Call main function with parsed arguments
		try:
			exit_code = main(args.endpoint, loglevel=args.loglevel, **params_dict)
			sys.exit(exit_code)
		except Exception as e:
			print(f"Unhandled exception: {e}")
			traceback.print_exc()
			sys.exit(1)
		