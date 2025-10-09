"""Main script for data collection and file operations."""

from pathlib import Path

from src.config.logging_config import setup_logging
from src.extract.ratings_data import fetch_ratings_data
from src.extract.weather_data import fetch_weather_data
from src.load.load_to_parquet import save_parquet

# Set up logging
logger = setup_logging(log_file="logs/data_collection.log")

def main():
    """
    Main function to collect ratings and weather data and save them to parquet.
    """
    try:        
        # # Collect ratings data
        # logger.info("Starting data collection process...")
        # ratings_df = fetch_ratings_data()
        
        # if ratings_df.empty:
        #     logger.warning("No data collected, exiting")
        #     return
        
        # # Save to parquet
        # output_path = Path("data/ratings_data.parquet")
        # save_parquet(ratings_df, output_path)
        
        # logger.info("Data collection and saving completed successfully!")

        # Collect weather data
        logger.info("Starting weather data collection process...")
        weather_df = fetch_weather_data()
        
        if weather_df.empty:
            logger.warning("No data collected, exiting")
            return
        
        # Save to parquet
        output_path = Path("data/weather_data.parquet")
        save_parquet(weather_df, output_path)
        
        logger.info("Data collection and saving completed successfully!")
        
    except Exception as e:
        logger.error(f"Main process failed: {e}")
        raise


if __name__ == "__main__":
    main()