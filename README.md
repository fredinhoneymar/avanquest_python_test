# Information
**Avanquest Data Engineer: Python Coding Test**
- API initial Url: https://api.football-data.org/
- API credentials: [config.yaml](./config.yaml)
- Client Application Name: Football Data Processing System v1.0.0

# Command Line Usage

The application provides a flexible command-line interface for data retrieval and processing.

### Syntax

```bash
python src/main.py <endpoint> [--params key=value [key=value ...]] [--loglevel LEVEL] [--test]
```

### Examples

```bash
# Fetch Premier League Standings
python src/main.py /competitions/PL/standings

# Fetch Premier League Standings for multiple seasons
python src/main.py /competitions/PL/standings --params season=[2020,2021,2022,2023]

# Enable Debug Logging
python src/main.py /competitions/PL/standings --loglevel DEBUG

# Run the Test Suite
python src/main.py --test
```

# Football Data Processing System <small style="font-size: .5em;">v1.0.0</small>

This app is a Python-based system designed to connect to the football-data.org API, process football data, and output it in a structured format.  
It is built with modularity and testability in mind, ensuring that each component can be independently further developed, reused and tested.

Targeted endpoint is **Premier League standings**. However, the system is designed to handle any available combinations of endpoints and filters.  
The system can also be easily extended to support any REST API endpoint, not just football data.

**Table of contents**
- [Architecture](#architecture)
- [Key Components](#key-components)
- [Workflow](#workflow)
- [Configuration](#configuration)
- [Optimization Strategies](#optimization-strategies)
- [Test Suite](#test-suite)
- [Historical Data Access Limitations](#historical-data-access-limitations)

## Architecture

The system follows a modular architecture with clear separation of concerns:

```
├── cache/
|
├── data/
|
├── logs/
|
├── src/
│	├── __init__.py				# Package initialization
│	├── apiconnector.py			# Handles API connectivity and caching
|	│── configuration.py		# Manages configuration settings
|	│── interfaces.py			# Defines interfaces
|	│── main.py					# Main entry point for the application
│	├── processors.py			# Processes and transforms data
│	├── reporter.py				# Handles data quality checks and reporting
│	└── utils.py				# Utility functions for common tasks
|
├── tests/
│	├── coverage_html
│	|	├── index.html			# HTML report of test coverage
│	|	└── ...
│	├── main_unittest.py		# Main entry point for the Test Suite
│	├── mockconfigprovider.py	# Shared test fixtures
│	├── ut_apiconnector.py		# Unit tests for API connector
│	└── ut_processors.py		# Unit tests for data processors
|
├── .coveragerc					# PyTest configuration
├── config.yaml					# Configuration file for the application
├── README.md					# Project documentation
└── requirements.txt			# Python package dependencies
```

## Key Components

- **APIConnector**: Singleton class handling API requests with retry logic, timeout handling, and caching
- **PremierLeagueDataProcessor**: Implementation for Premier League data processing
- **DataQualityChecker**: Validates and scores data quality
- **ConfigProvider**: Configuration management and logging

## Workflow

1. **Data Acquisition**
   - System connects to football-data.org API
   - Makes requests with proper headers, error handling, and retries
   - Implements caching to reduce API calls and improve performance

2. **Data Processing**
   - Raw API data is validated for structure and content
   - Data lineage is added to track sources and transformations
   - Quality checks are performed to ensure data integrity

3. **Data Output**
   - Processed data is saved to CSV files
   - Quality reports generated alongside data
   - Logging information is recorded for debugging and auditing

## Configuration

The system is configurable via a YAML file (`config.yaml`).  
The Test Suite is configurable via a PyTest setup file (`.coveragerc`).


## Optimization Strategies

The system implements several optimization strategies to improve performance, reduce resource consumption, and enhance reliability:

1. **File-based Caching**
	- ***Hash-based Indexing***: Uses MD5 hashing of request parameters for efficient cache retrieval
	- ***Automatic Cache Management***: Expired entries (configurable via `cache_ttl`) are automatically cleaned up during initialization

2. **Parallel Processing**
	- ***Concurrent API Calls***: Uses ThreadPoolExecutor to make multiple API requests simultaneously
	- ***Configurable Concurrency***: Number of worker threads can be adjusted based on system capabilities

3. **Memory Optimization**
	- ***Batch Processing***: CSV data is written in configurable batches instead of loading all records into memory
	- ***Resource Cleanup***: Proper cleanup of temporary resources to prevent memory leaks

4. **Network Resilience**
	- ***Exponential Backoff***: Retry attempts use exponential backoff algorithm (2^retries + 1) to avoid overwhelming the API
	- ***Rate Limiting Compliance***: Respects the API's Retry-After headers when rate limits are hit

5. **Design Patterns for Efficiency**
	- ***Singleton Pattern***: APIConnector uses the Singleton pattern to ensure only one instance exists, preventing duplicate connections
	- ***Interfaces***: Standardized creation of objects to ensure proper implementation of methods

6. **Resource Management**
	- ***Exception Handling***: Robust error handling to ensure resources are properly cleaned up
	- ***Defensive Programming***: Validation of inputs and state to prevent crashes and resource waste

These optimization strategies work together to ensure the system can handle large datasets efficiently while maintaining reliability and responsiveness.


## Test Suite

1. **Test Coverage**
	- Unit tests cover: 
		- APIConnector
		- DataProcessor
	- Current coverage: 90.62% (target: 80%)

2. **Test Organization**
	- Tests separated by component (apiconnector, processors)
	- Shared fixtures via mockconfigprovider.py
	- Independent test execution with automatic resource cleanup

3. **HTML Report**
	- Generated using pytest-html
	- Accessible in the `tests/coverage_html` directory after running tests



## Historical Data Access Limitations

### Tier-Based Access

- **Tier One**: Only provides access to seasons 2023 and 2024 data with standard refresh rates
  - Premier League standings, teams, and upcoming fixtures
  - Real-time score updates
  - Player statistics for current season

- **Tier Two**: Extended historical access and additional features
  - Complete match archives
  - Historical player statistics
  - Seasonal comparisons

### Issue with Historical Data Access
The current subscription tier (Tier One) limits access to historical data.  
This behavior is described in [403_limitations.md](./403_limitations.md), 
which also includes correspondence with Football Data API developer Daniel.

### Implications for the Assignment
The CSV file provided as an output instance is restricted to PL seasons 2023-24 and 2024-25 (120 records):
```log
(AvanquestPythonTest) root@DESKTOP-FCTK9TQ:/Avanquest_TEST/python/test/src# python main.py /competitions/PL/standings --params season=[2023,2024]

2025-05-11 14:12:12,946 - INFO - Configuration loaded from /Avanquest_TEST/python/test/config.yaml
2025-05-11 14:12:12,955 - INFO - Making request GEThttps://api.football-data.org/v4/competitions/PL/standings?season=2023
2025-05-11 14:12:12,955 - INFO - Making request GEThttps://api.football-data.org/v4/competitions/PL/standings?season=2024
2025-05-11 14:12:12,072 - INFO - Data fetched with status code 200 for {'season': 2024}
2025-05-11 14:12:12,124 - INFO - Data fetched with status code 200 for {'season': 2023}
2025-05-11 14:12:12,125 - INFO - Processed standings data for season 2024
2025-05-11 14:12:12,126 - INFO - Processed standings data for season 2023
2025-05-11 14:12:12,127 - INFO - Added data lineage information
2025-05-11 14:12:12,127 - INFO - Successfully processed 120 team records from 2 dataset(s)
2025-05-11 14:12:12,136 - INFO - Data saved to: /Avanquest_TEST/python/test/data/stats_20250511_141212.csv
2025-05-11 14:12:12,191 - INFO - Data quality report saved to: /Avanquest_TEST/python/test/data/data_quality_report_20250511_141212.json
2025-05-11 14:12:12,192 - WARNING - Quality issues found: {'INFO': 5}
