"""Weather data processing utilities."""

import pandas as pd
import logging
from typing import Dict, Any

from ..utils.exceptions import DataProcessingError


logger = logging.getLogger(__name__)


class WeatherTransformer:
    """
    Processes and cleans weather data.
    
    This class handles all data processing operations for weather data,
    including data formatting and validation.
    """
    
    def __init__(self):
        """Initialize weather processor."""
        pass
    
    def format_data(self, weather_df: pd.DataFrame) -> pd.DataFrame:
        """
        Format the weather dataframe.

        Parameters
        ----------
        weather_df : pandas.DataFrame
            The raw weather data in a DataFrame

        Returns
        -------
        pandas.DataFrame
            The formatted weather data in a DataFrame

        Raises
        ------
        DataProcessingError
            If the data processing fails
        """
        try:
            # Create a copy of df
            df = weather_df.copy()

            # Add sunrise and sunset time columns
            if 'sunrise' in df.columns:
                df["sunrise_time"] = pd.to_datetime(df['sunrise'], unit='s', utc=True).dt.tz_convert("Europe/Brussels")
            if 'sunset' in df.columns:
                df["sunset_time"] = pd.to_datetime(df['sunset'], unit='s', utc=True).dt.tz_convert("Europe/Brussels")

            # Remove timezone from date column (used for merge)
            df["date"] = df["date"].dt.tz_localize(None)

            logger.info(f"Weather data formatting complete! Processed {len(df)} records.")
            return df
        
        except Exception as e:
            error_message = f"Error formatting weather data: {e}"
            logger.error(error_message)
            raise DataProcessingError(error_message) from e