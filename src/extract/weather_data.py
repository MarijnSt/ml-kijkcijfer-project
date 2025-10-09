import pandas as pd
import logging
from datetime import datetime, timedelta

from ..config.settings import DEFAULT_START_DATE, DATE_FORMAT, LATEST_OFFSET_DAYS
from ..utils.exceptions import DataProcessingError, ValidationError
from ..data_sources import WeatherClient
from ..transform import WeatherTransformer

logger = logging.getLogger(__name__)

def _determine_data_type(start_date: str) -> str:
    """
    Determine if we are fetching historical or forecast data.

    Parameters:
    ----------
    start_date: str
        The start date of the date range (format: YYYY-MM-DD)

    Returns:
    -------
    str
        The type of data to fetch (historical or forecast)

    Raises:
    -------
    ValidationError
        If the date format is invalid
    """
    today = datetime.now().date()

    try:
        start_date_parsed = datetime.strptime(start_date, DATE_FORMAT).date()
        if start_date_parsed > today:
            return "forecast"
        else:
            return "historical"
            
    except ValueError as e:
        raise ValidationError(f"Invalid start date format: {start_date}. Expected format: YYYY-MM-DD") from e

def fetch_weather_data(
    start_date: str = None, 
    end_date: str = None,
) -> pd.DataFrame:
    """
    Fetch weather data from the Open-Meteo API.

    Parameters:
    ----------
    start_date: str
        The start date of the date range (format: YYYY-MM-DD)
    end_date: str
        The end date of the date range (format: YYYY-MM-DD)

    Returns:
    -------
    df: pandas.DataFrame
        The weather data in DataFrame format

    Raises:
    -------
    ValidationError
        If the date format is invalid
    DataProcessingError
        If the data processing fails
    """

    # Set start and end date. Use config defaults if not provided
    start_date = start_date or DEFAULT_START_DATE
    end_date = end_date or "latest"

    # Determine if we are fetching historical or forecast data
    data_type = _determine_data_type(start_date)

    logger.info(f"Fetching weather data from {start_date} to {end_date}")

    try:
        # Initialize weather client and transformer
        weather_client = WeatherClient()
        weather_transformer = WeatherTransformer()

        # Convert end date if it is "latest"
        if end_date == "latest":
            end_date = datetime.now() - timedelta(days=LATEST_OFFSET_DAYS)
            end_date = end_date.strftime(DATE_FORMAT)
            logger.info(f"Using 'latest' end date: {end_date}")

        # Get data for date range
        if data_type == "historical":
            weather_data = weather_client.get_historical_data(start_date, end_date)
        else:
            weather_data = weather_client.get_forecast_data(start_date, end_date)

        logger.info(f"Weather data collection complete! Total records: {len(weather_data)}")

        if not weather_data.empty:
            logger.info(f"Creating DataFrame from {len(weather_data)} records")
            df = pd.DataFrame(weather_data)

            # Format data
            df = weather_transformer.format_data(df)
            
            logger.info(f"Weather data collection complete! Total records: {len(df)}")
            return df
        else:
            logger.warning("No data collected for date range")
            return pd.DataFrame()

    except Exception as e:
        error_message = f"Error fetching weather data. {e}"
        logger.error(error_message)
        raise DataProcessingError(error_message) from e