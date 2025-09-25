import requests
import requests_cache
from retry_requests import retry
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO, # Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s', # Timestamp, level, message. Example: 2024-01-15 14:30:25,123 - INFO - Fetching data from API for date: 2024-1-15
    handlers=[
        logging.FileHandler('ratings_data.log'), # Log to file
        logging.StreamHandler() # Log to console
    ]
)
logger = logging.getLogger(__name__) # Creates logger instance for this module

# Custom exceptions
class RatingsDataError(Exception):
    """Base exception for ratings data operations"""
    pass

class APIError(RatingsDataError):
    """Exception raised when API requests fail"""
    pass

class DataProcessingError(RatingsDataError):
    """Exception raised when data processing fails"""
    pass

class ValidationError(RatingsDataError):
    """Exception raised when data validation fails"""
    pass


def get_cim_tv_data(date: str, session: requests.Session) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch data from CIM TV API and convert it to a pandas DataFrame.

    Parameters:
    ----------
    date: str
        The date in format YYYY-M-D
    session: requests.Session
        The cached session to use for requests

    Returns:
    -------
    list or None
        List of dictionaries (records) or None if error

    Raises:
    -------
    APIError
        If the API request fails
    ValidationError
        If the date format is invalid
    """

    # Validate the date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"Invalid date format: {date}. Expected format: YYYY-M-D")

    # Construct the API URL
    api_url = f"https://api.cim.be/api/cim_tv_public_results_daily_views?dateDiff={date}&reportType=north"

    logger.info(f"Fetching data from API for date: {date}")

    try:
        # Make the API request using the provided session
        response = session.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Get the ratings data from the response
        ratings_data = data.get('hydra:member', [])

        if not ratings_data:
            logger.warning(f"No data found for date: {date}")
            return None

        # Process the data
        processed_records = []
        for record in ratings_data:
            try:
                # Keep only relevant columns and rename them
                processed_record = {
                    "show": record.get("description"),
                    "channel": record.get("channel"),
                    "date": record.get("dateDiff"),
                    "start": record.get("startTime"),
                    "duration": record.get("rLength"),
                    "viewers": record.get("rateInK"),
                }
                processed_records.append(processed_record)
            except Exception as e:
                logger.error(f"Error processing record for date: {date}: {e}")
                continue

        logger.info(f"Successfully processed {len(processed_records)} records for date: {date}")
        return processed_records
    
    except Exception as e:
        error_message = f"Error fetching data for date: {date}: {e}"
        logger.error(error_message)
        raise APIError(error_message) from e


def correct_start_times(ratings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Correct the dates of the ratings data.
    Some records have a starting time of 24:xx:xx or 25:xx:xx with the wrong date. 
    They should get moved to the next day.

    Parameters:
    ----------
    ratings_df: pandas.DataFrame
        The ratings data in a DataFrame

    Returns:
    -------
    ratings_df_corrected: pandas.DataFrame
        The corrected ratings data in a DataFrame

    Raises:
    -------
    DataProcessingError
        If the data processing fails
    """
    try:
        # Create a copy to avoid modifying the original during iteration
        ratings_df_corrected = ratings_df.copy()

        # Get indices of faulty records
        faulty_indices = ratings_df[
            ratings_df["start"].str.startswith("24:") | 
            ratings_df["start"].str.startswith("25:")
        ].index

        logger.info(f"Found {len(faulty_indices)} faulty 'start' records to correct")

        # Process each faulty record individually
        corrected_count = 0
        for idx in faulty_indices:
            try:
                start_time = ratings_df.loc[idx, "start"]
                original_date = ratings_df.loc[idx, "date"]
                
                if start_time.startswith("24:"):
                    # Move to next day and convert 24:xx:xx to 00:xx:xx
                    new_date = pd.to_datetime(original_date) + pd.Timedelta(days=1)
                    new_start_time = start_time.replace("24:", "00:", 1)
                    logger.debug(f"Record {idx}: {original_date} {start_time} → {new_date.strftime('%Y-%m-%d')} {new_start_time}")
                    
                elif start_time.startswith("25:"):
                    # Move to next day and convert 25:xx:xx to 01:xx:xx
                    new_date = pd.to_datetime(original_date) + pd.Timedelta(days=1)
                    new_start_time = start_time.replace("25:", "01:", 1)
                    logger.debug(f"Record {idx}: {original_date} {start_time} → {new_date.strftime('%Y-%m-%d')} {new_start_time}")
                
                else:
                    logger.warning(f"Unexpected start time format: {start_time}")
                    continue
                
                # Update the corrected dataframe
                ratings_df_corrected.loc[idx, "date"] = new_date
                ratings_df_corrected.loc[idx, "start"] = new_start_time
                corrected_count += 1

            except Exception as e:
                logger.error(f"Error correcting start time for record {idx}: {e}")
                continue

        logger.info(f"\nCorrection complete! Updated {corrected_count} 'start' records.")
        return ratings_df_corrected
    
    except Exception as e:
        error_message = f"Error correcting start times: {e}"
        logger.error(error_message)
        raise DataProcessingError(error_message) from e

def normalize_channel_names(ratings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Channel names have changed over the years. 
    This function normalizes the channel names.

    Parameters:
    ----------
    ratings_df: pandas.DataFrame
        The ratings data in a DataFrame

    Returns:
    -------
    df: pandas.DataFrame
        The normalized ratings data in a DataFrame

    Raises:
    -------
    DataProcessingError
        If the data processing fails
    """
    try:
        # Create a copy of df
        df = ratings_df.copy()

        # Normalize the channel names
        channel_mappings = {
            "EEN": ["EEN", "VRT 1"],
            "CANVAS": ["Canvas", "CANVAS", "VRT CANVAS"],
            "KETNET": ["KETNET", "OP 12"],
            "PLAY4": ["VIER", "PLAY4"],
            "PLAY5": ["VIJF", "PLAY5"],
            "PLAY6": ["ZES", "PLAY6"],
            "VTM2": ["Q2", "VTM2"],
            "VTM3": ["VITAYA", "VTM3"],
            "VTM4": ["CAZ", "VTM4"],
            "EEN": ["EEN,VTM,PLAY4", "EEN, VTM, PLAY", "VRT 1/VTM/Play4"],
            "PRO LEAGUE 1": ["ELEVEN PRO LEAGUE 1 NL", "DAZN PRO LEAGUE 1 (NL)"]
        }
        
        normalization_count = 0
        for normalized_name, variants in channel_mappings.items():
            mask = df["channel"].isin(variants)
            if mask.any():
                count = mask.sum()
                df.loc[mask, "channel"] = normalized_name
                normalization_count += count
                logger.debug(f"Normalized {count} records to channel '{normalized_name}'")
        
        logger.info(f"Channel normalization complete! Updated {normalization_count} records.")
        return df
        
    except Exception as e:
        error_message = f"Error normalizing channel names: {e}"
        logger.error(error_message)
        raise DataProcessingError(error_message) from e

def format_data(ratings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Format the columns of the ratings dataframe.

    Parameters:
    ----------
    ratings_df: pandas.DataFrame
        The ratings data in a DataFrame

    Returns:
    -------
    df: pandas.DataFrame
        The formatted ratings data in a DataFrame

    Raises:
    -------
    DataProcessingError
        If the data processing fails
    """
    try:
        # Create a copy of df
        df = ratings_df.copy()
        original_count = len(df)

        # Convert 'date' to datetime
        df["date"] = pd.to_datetime(df["date"])
        logger.debug("Converted 'date' to datetime.")

        # Fix faulty 'start' values
        df = correct_start_times(df)

        # Convert 'start' to datetime and convert errors to NaT
        df["start"] = pd.to_datetime(df["start"], format='%H:%M:%S', errors='coerce')
        invalid_start_count = len(df[df["start"].isna()])
        if invalid_start_count > 0:
            logger.warning(f"Found {invalid_start_count} invalid 'start' values. Will be dropped.")

        # Drop rows with NaT 'start' values
        df = df.dropna(subset=['start'])

        # Combine 'start with 'date' to create proper datetime
        df["start"] = [pd.Timestamp.combine(d, t) for d, t in zip(df['date'], df["start"].dt.time)]
        logger.debug("Combined 'start' and 'date' columns.")

        # Convert 'duration' to timedelta
        df["duration"] = pd.to_timedelta(df["duration"])
        logger.debug("Converted 'duration' to timedelta.")

        # Replace 'viewers' data dots and commas
        df["viewers"] = df["viewers"].str.replace(".", "").str.replace(",", ".")

        # Convert 'viewers' to numeric (errors converted to NaN)
        df["viewers"] = pd.to_numeric(df["viewers"], errors='coerce')
        invalid_viewers_count = len(df[df["viewers"].isna()])
        if invalid_viewers_count > 0:
            logger.warning(f"Found {invalid_viewers_count} invalid 'viewers' values. Will be dropped.")

        # Drop rows with NaN 'viewers' values
        df = df.dropna(subset=['viewers'])

        # Convert 'viewers' to int
        df["viewers"] = df["viewers"].astype(int)

        # Normalize channel names
        df = normalize_channel_names(df)

        final_count = len(df)
        dropped_count = original_count - final_count
        if dropped_count > 0:
            logger.info(f"Data formatting complete! Dropped {dropped_count} records, {final_count} records remaining.")
        else:
            logger.info(f"Data formatting complete! All {final_count} records processed successfully.")

        return df
    
    except Exception as e:
        error_message = f"Error formatting data: {e}"
        logger.error(error_message)
        raise DataProcessingError(error_message) from e

def get_ratings_data(start_date: str = "2016-10-1", end_date: str = "latest") -> pd.DataFrame:
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
    APIError
        If the API request fails
    DataProcessingError
        If the data processing fails
    """
    logger.info(f"Starting data collection from {start_date} to {end_date}")

    try:
        # Setup request session with cache and retry on error (once for all requests)
        cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        logger.debug("Initialized cached session with retry logic.")

        # Convert string dates to datetime objects
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValidationError(f"Invalid start date format: {start_date}. Expected format: YYYY-MM-DD") from e

        if end_date == "latest":
            end_date = datetime.now() - timedelta(days=2)
            logger.info(f"Using 'latest' end date: {end_date.strftime('%Y-%m-%d')}")
        else:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError as e:
                raise ValidationError(f"Invalid end date format: {end_date}. Expected format: YYYY-MM-DD") from e

        # Initialize list to collect all records
        all_records = []
        processed_count = 0
        failed_count = 0

        # Loop through dates in the range
        current_date = start_date
        while current_date <= end_date:
            try:
                # Format date back to string (API format: YYYY-M-D)
                date_str = current_date.strftime("%Y-%-m-%-d")
                logger.info(f"Processing date: {date_str}")

                # Get data for current date using the shared session
                daily_records = get_cim_tv_data(date_str, retry_session)

                # Add to list
                if daily_records:
                    all_records.extend(daily_records)
                    logger.info(f"✓ Added {len(daily_records)} records")
                else:
                    logger.warning(f"✗ No data for date: {date_str}")

                processed_count += 1

                # Add a delay between requests to avoid rate limiting
                time.sleep(1)
                

            except Exception as e:
                logger.error(f"Error processing date {date_str}: {str(e)}")
                failed_count += 1
                time.sleep(5)
            
            finally:
                # Move to next day
                current_date += timedelta(days=1)
        
        logger.info(f"Data collection complete! Processed {processed_count} dates, {failed_count} dates failed.")

        # Create DataFrame once at the end
        if all_records:
            logger.info(f"Creating DataFrame from {len(all_records)} records")
            df = pd.DataFrame(all_records)
            
            # Format data
            df = format_data(df)

            # Drop rows with missing values
            df = df.dropna()
            
            logger.info(f"Data collection complete! Total records: {len(df)}")
            return df
        else:
            logger.warning("No data collected from any date")
            return pd.DataFrame()
    
    except Exception as e:
        error_message = f"Error getting ratings data: {e}"
        logger.error(error_message)
        raise DataProcessingError(error_message) from e

def create_ratings_parquet(output_path: Union[str, Path] = "ratings_data.parquet") -> Path:
    """
    Create a parquet file from the ratings data.

    Parameters:
    ----------
    output_path: Union[str, Path]
        Path where the parquet file will be saved

    Returns:
    -------
    Path
        Path where the parquet file is saved
        
    Raises:
    -------
    DataProcessingError
        If the data processing fails
    """
    
    try:
        output_path = Path(output_path)
        logger.info(f"Creating parquet file at {output_path}")

        df = get_ratings_data()
        
        if df.empty:
            logger.warning("No data saved to parquet file")
            return output_path
        
        df.to_parquet(output_path)

        logger.info(f"Succesfully created {output_path} with {len(df)} records")
        return output_path
    
    except Exception as e:
        error_message = f"Error creating ratings parquet file: {e}"
        logger.error(error_message)
        raise DataProcessingError(error_message) from e


if __name__ == "__main__":
    try:
        create_ratings_parquet()
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise