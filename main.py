from services.api_client import get_matches
from utils.data_processing import process_matches, save_to_csv
from config.settings import SEASON_YEARS
from config.logging_config import setup_logger

# Initialize the logger
logger = setup_logger(__name__)

def run_pipeline_for_year(year, logger):
    """Executes the data pipeline for a specific season"""
    logger.info(f"... Starting pipeline for the {year}")
    
    # Get the matches for the year
    matches = get_matches(year, logger)
    
    if matches:
        # Process the matches and save the data to CSV
        stats = process_matches(matches, logger)
        save_to_csv(stats, year, logger)
        logger.info(f" Pipeline completed for {year}")
    else:
        logger.warning(f"⚠ No matches found for the {year}")

def main():
    """Main function to run the pipeline for multiple seasons"""
    for year in SEASON_YEARS:
        run_pipeline_for_year(year, logger) 

if __name__ == "__main__":
    main()
