"""Main script for data collection and file operations."""

import logging
from pathlib import Path

from .config.logging_config import setup_logging
from .extract.ratings_data import fetch_ratings_data
from .load.load_to_parquet import save_parquet


# Set up logging
logger = setup_logging()


def main():
    """
    Main function to collect ratings data and save to parquet.
    """
    try:        
        # Collect ratings data
        logger.info("Starting data collection process...")
        ratings_df = fetch_ratings_data("2025-01-01", "2025-01-03")
        
        if ratings_df.empty:
            logger.warning("No data collected, exiting")
            return
        
        # Save to parquet
        output_path = Path("ratings_data_test.parquet")
        save_parquet(ratings_df, output_path)
        
        logger.info("Data collection and saving completed successfully!")
        
    except Exception as e:
        logger.error(f"Main process failed: {e}")
        raise


if __name__ == "__main__":
    main()