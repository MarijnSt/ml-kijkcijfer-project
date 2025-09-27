"""Weather API client."""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

import openmeteo_requests
import pandas as pd

from ..config.settings import WEATHER_API, WEATHER_LOCATION, WEATHER_VARIABLES, DATE_FORMAT
from ..utils.exceptions import APIError, ValidationError, ValidationError
from ..utils.session_manager import SessionManager


logger = logging.getLogger(__name__)


class WeatherClient:
    """
    Client for Weather API.
    
    This class handles all interactions with the Open-Meteo weather API,
    including data fetching, error handling, and response processing.
    """
    
    def __init__(self):
        """Initialize weather client with configuration."""
        self.config = WEATHER_API
        self.session_manager = SessionManager(self.config)
        self.location = WEATHER_LOCATION
        self.variables = WEATHER_VARIABLES
    
    def get_historical_data(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Get historical weather data from the Open-Meteo API.
        
        The location is fixed to Ukkel.

        Parameters
        ----------
        start_date : str
            The start date of the weather data to get (format: YYYY-MM-DD)
        end_date : str
            The end date of the weather data to get (format: YYYY-MM-DD)

        Returns
        -------
        pandas.DataFrame or None
            The weather data or None if no data

        Raises
        ------
        APIError
            If the API request fails
        ValidationError
            If the date format is invalid
        """
        # Validate date formats
        try:
            datetime.strptime(start_date, DATE_FORMAT)
            datetime.strptime(end_date, DATE_FORMAT)
        except ValueError as e:
            raise ValidationError(f"Invalid date format. Expected format: YYYY-MM-DD") from e

        logger.info(f"Fetching weather data from {start_date} to {end_date}")

        try:
            # Setup the Open-Meteo API client
            openmeteo = openmeteo_requests.Client(session = self.session_manager.session)

            # Prepare API parameters
            params = {
                "latitude": self.location["latitude"],
                "longitude": self.location["longitude"],
                "start_date": start_date,
                "end_date": end_date,
                "daily": self.variables,
            }

            # Make API request
            responses = openmeteo.weather_api(self.config["base_url"], params=params)
            response = responses[0]

            # Process daily data
            daily = response.Daily()
            
            # Extract all variables
            daily_data = {"date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            )}

            # Map variables to their data
            for i, var in enumerate(self.variables):
                daily_data[var] = daily.Variables(i).ValuesAsNumpy()

            # Add sunrise and sunset time columns
            if 'sunrise' in daily_data:
                daily_data["sunrise_time"] = pd.to_datetime(daily_data['sunrise'], unit='s')
            if 'sunset' in daily_data:
                daily_data["sunset_time"] = pd.to_datetime(daily_data['sunset'], unit='s')

            df = pd.DataFrame(data=daily_data)
            logger.info(f"Successfully processed {len(df)} weather records")
            return df

        except Exception as e:
            error_message = f"Error fetching weather data: {e}"
            logger.error(error_message)
            raise APIError(error_message) from e