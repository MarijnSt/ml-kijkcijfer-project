import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import Optional

from ..config.settings import DATE_FORMAT, DEFAULT_START_DATE, LATEST_OFFSET_DAYS, API_DATE_FORMAT, CIM_TV_API
from ..data_sources import CIMTVClient
from ..transform import RatingsTransformer
from ..utils.exceptions import ValidationError, DataProcessingError

logger = logging.getLogger(__name__)

def fetch_ratings_data(
    start_date: str = None,
    end_date: str = None
) -> pd.DataFrame:
    """
    Fetch ratings data from CIM TV API for a given date range.

    Parameters:
    ----------
    start_date: str
        The start date of the date range (format: YYYY-MM-DD)
    end_date: str
        The end date of the date range (format: YYYY-MM-DD)
        default: "latest" (two days ago is the latest possible date)

    Returns:
    -------
    df: pandas.DataFrame
        The ratings data in DataFrame format

    Raises:
    -------
    ValidationError
        If the date format is invalid
    DataProcessingError
        If the data processing fails
    """

    # Set start and end date.Use config defaults if not provided
    start_date = start_date or DEFAULT_START_DATE
    end_date = end_date or "latest"

    logger.info(f"Fetching ratings data from {start_date} to {end_date}")

    try:
        # Initialize CIM TV client and transformer
        cim_tv_client = CIMTVClient()
        ratings_transformer = RatingsTransformer()

        # Convert string dates to datetime objects
        try:
            start_date = datetime.strptime(start_date, DATE_FORMAT)
        except ValueError as e:
            raise ValidationError(f"Invalid start date format: {start_date}. Expected format: YYYY-MM-DD") from e

        if end_date == "latest":
            end_date = datetime.now() - timedelta(days=LATEST_OFFSET_DAYS)
            logger.info(f"Using 'latest' end date: {end_date.strftime('%Y-%m-%d')}")
        else:
            try:
                end_date = datetime.strptime(end_date, DATE_FORMAT)
            except ValueError as e:
                raise ValidationError(f"Invalid end date format: {end_date}. Expected format: YYYY-MM-DD") from e

        # Initialize tracking variables
        all_records = []
        processed_count = 0
        failed_count = 0

        # Loop through dates in the range
        current_date = start_date
        while current_date <= end_date:
            try:
                # Format date back to string (API format: YYYY-M-D)
                date_str = current_date.strftime(API_DATE_FORMAT)
                logger.info(f"Processing date: {date_str}")

                # Get data for current date
                daily_records = cim_tv_client.get_data(date_str)

                # Add to list
                if daily_records:
                    all_records.extend(daily_records)
                    logger.info(f"✓ Added {len(daily_records)} records")
                else:
                    logger.warning(f"✗ No data for date: {date_str}")

                processed_count += 1

                # Add a delay between requests to avoid rate limiting
                time.sleep(CIM_TV_API["request_delay"])

            except Exception as e:
                logger.error(f"Error processing date {date_str}: {str(e)}")
                failed_count += 1
                time.sleep(CIM_TV_API["error_delay"])
            
            finally:
                # Move to next day
                current_date += timedelta(days=1)
        
        logger.info(f"Data collection complete! Processed {processed_count} dates, {failed_count} dates failed.")

        # Convert list to DataFrame and format data
        if all_records:
            logger.info(f"Creating DataFrame from {len(all_records)} records")
            df = pd.DataFrame(all_records)
            
            # Format data
            df = ratings_transformer.format_data(df)

            # Drop rows with missing values
            df = df.dropna()
            
            logger.info(f"Ratings data collection complete! Total records: {len(df)}")
            return df
        else:
            logger.warning("No data collected from any date")
            return pd.DataFrame()
    
    except Exception as e:
        error_message = f"Error getting ratings data: {e}"
        logger.error(error_message)
        raise DataProcessingError(error_message) from e