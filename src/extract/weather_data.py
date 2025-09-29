import pandas as pd
import logging

from ..config.settings import DEFAULT_START_DATE
from ..utils.exceptions import DataProcessingError
from ..data_sources import WeatherClient

logger = logging.getLogger(__name__)

def fetch_weather_data(
    start_date: str = None, 
    end_date: str = None
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

    logger.info(f"Fetching weather data from {start_date} to {end_date}")

    try:
        # Initialize weather client and transformer
        weather_client = WeatherClient()
        #weather_transformer = WeatherTransformer()

        # Get data for date range
        weather_data = weather_client.get_historical_data(start_date, end_date)

        logger.info(f"Weather data collection complete! Total records: {len(weather_data)}")

        if not weather_data.empty:
            logger.info(f"Creating DataFrame from {len(weather_data)} records")
            df = pd.DataFrame(weather_data)
            
            logger.info(f"Weather data collection complete! Total records: {len(df)}")
            return df
        else:
            logger.warning("No data collected for date range")
            return pd.DataFrame()

    except Exception as e:
        error_message = f"Error fetching weather data: {e}"
        logger.error(error_message)
        raise DataProcessingError(error_message) from e