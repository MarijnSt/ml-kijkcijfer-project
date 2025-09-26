"""Weather data processing utilities."""

import pandas as pd
import logging
from typing import Dict, Any

from ..utils.exceptions import DataProcessingError


logger = logging.getLogger(__name__)


class WeatherProcessor:
    """
    Processes and cleans weather data.
    
    This class handles all data processing operations for weather data,
    including data formatting and validation.
    """
    
    def __init__(self):
        """Initialize weather processor."""
        pass
    
    def format_weather_data(self, weather_df: pd.DataFrame) -> pd.DataFrame:
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
            original_count = len(df)

            # Convert sunrise and sunset to datetime
            if 'sunrise' in df.columns:
                df['sunrise_time'] = pd.to_datetime(df['sunrise'], unit='s')
            if 'sunset' in df.columns:
                df['sunset_time'] = pd.to_datetime(df['sunset'], unit='s')

            # Ensure date column is datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            logger.info(f"Weather data formatting complete! Processed {len(df)} records.")
            return df
        
        except Exception as e:
            error_message = f"Error formatting weather data: {e}"
            logger.error(error_message)
            raise DataProcessingError(error_message) from e