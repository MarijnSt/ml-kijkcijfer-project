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


    def validate_date(self, date: str) -> None:
        """
        Validate the date.

        Parameters
        ----------
        date : str
            The date to validate (format: YYYY-MM-DD)

        Raises
        ------
        ValidationError
            If the date format is invalid
        """
        try:
            datetime.strptime(date, DATE_FORMAT)
        except ValueError as e:
            raise ValidationError(f"Invalid date: {date}. Expected format: YYYY-MM-DD") from e
    

    def _fetch_weather_data(
        self, 
        start_date: str, 
        end_date: str,
        api_endpoint: str
    ) -> Optional[pd.DataFrame]:
        """
        Get historical or forecastweather data from the Open-Meteo API.
        
        The location is fixed to Ukkel.

        Parameters
        ----------
        start_date : str
            The start date of the weather data to get (format: YYYY-MM-DD)
        end_date : str
            The end date of the weather data to get (format: YYYY-MM-DD)
        api_endpoint : str
            The API endpoint to use (historical or forecast)

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
        self.validate_date(start_date)
        self.validate_date(end_date)

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
            responses = openmeteo.weather_api(api_endpoint, params=params)
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
                # Handle sunrise and sunset (index 4 and 5)
                if i == 4 or i == 5:
                    daily_data[var] = daily.Variables(i).ValuesInt64AsNumpy()
                else:
                    daily_data[var] = daily.Variables(i).ValuesAsNumpy()

            # Add sunrise and sunset time columns
            if 'sunrise' in daily_data:
                daily_data["sunrise_time"] = pd.to_datetime(daily_data['sunrise'], unit='s', utc=True).tz_convert("Europe/Brussels")
            if 'sunset' in daily_data:
                daily_data["sunset_time"] = pd.to_datetime(daily_data['sunset'], unit='s', utc=True).tz_convert("Europe/Brussels")

            df = pd.DataFrame(data=daily_data)
            logger.info(f"Successfully processed {len(df)} weather records")
            return df

        except Exception as e:
            error_message = f"Error fetching weather data: {e}"
            logger.error(error_message)
            raise APIError(error_message) from e


    def get_historical_data(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Get historical weather data from the Open-Meteo API.
        """
        logger.info(f"Fetching historical weather data from {start_date} to {end_date}")
        
        return self._fetch_weather_data(start_date, end_date, self.config["base_url_historical"])


    def get_forecast_data(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Get forecast weather data from the Open-Meteo API.
        """
        logger.info(f"Fetching forecast weather data from {start_date} to {end_date}")
        
        return self._fetch_weather_data(start_date, end_date, self.config["base_url_forecast"])