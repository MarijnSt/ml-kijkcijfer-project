import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

from ..utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    This class handles all data transformations for the model data.

    Includes:
    - Merging ratings and weather data
    - Feature engineering
    - Selecting features
    """
    
    # TODO: drop certain features based on feature importance
    FEATURES_LIST = [
        "show", "channel", "viewers",
        "year", "month", "day_of_week", "week",
        "covid_19", "lockdown_1", "lockdown_2",
        "start_of_program_hour", "end_of_program_hour", "duration",
        "in_primetime", "ends_in_primetime", "starts_in_primetime",
        "has_commercials",
        "sunrise_delta_start", "sunrise_delta_end", "sunset_delta_start", "sunset_delta_end",
        "sunrise_time", "sunset_time",
        "weather_code", "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
        "daylight_duration", "sunshine_duration", 
        "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours", 
        "wind_speed_10m_max", "wind_gusts_10m_max",
    ]

    def merge_ratings_and_weather_data(self, ratings_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge ratings and weather data.

        Parameters
        ----------
        ratings_df : pandas.DataFrame
            The ratings data in a DataFrame
        weather_df : pandas.DataFrame
            The weather data in a DataFrame

        Returns
        -------
        pandas.DataFrame
            The merged data in a DataFrame

        Raises
        ------
        DataProcessingError
            If the data processing fails
        """
        try:
            # Merge ratings and weather data
            df = pd.merge(ratings_df, weather_df, on="date", how="inner")

            return df
            
        except Exception as e:
            error_message = f"Error merging ratings and weather data: {e}"
            logger.error(error_message)
            raise DataProcessingError(error_message) from e


    def create_new_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create new features based on existing data.

        Parameters
        ----------
        data : pandas.DataFrame
            The data to create new features from

        Returns
        -------
        pandas.DataFrame
            The data with new features

        Raises
        ------
        DataProcessingError
            If the data processing fails
        """
        try:
            # Create a copy of df
            df = data.copy()

            # Get year, month, day of week and week from date
            df["year"] = df["date"].dt.year
            df["month"] = df["date"].dt.month
            df["day_of_week"] = df["date"].dt.day_of_week
            df["week"] = df["date"].dt.isocalendar().week

            # Covid features: based on dates from Belgium (when covid got here, when the lockdowns happened)
            df["covid_19"] = np.where((df["date"] >= "2020-02-04") & (df["date"] <= "2022-03-13"), 1, 0)
            df["lockdown_1"] = np.where((df["date"] >= "2020-03-13") & (df["date"] <= "2020-06-08"), 1, 0)
            df["lockdown_2"] = np.where((df["date"] >= "2020-10-30") & (df["date"] <= "2021-04-19"), 1, 0)

            # Ending of program
            df["end_of_program"] = df["start"] + df["duration"]

            # Start and end of program
            df["start_of_program_hour"] = df["start"].dt.hour
            df["end_of_program_hour"] = df["end_of_program"].dt.hour

            # Duration of program (in minutes)
            df["duration"] = np.round(df["duration"].dt.total_seconds() / 60)
            df["duration"] = df["duration"].astype(int)

            # Primetime features
            df["in_primetime"] = np.where((df["start_of_program_hour"] >= 20) & (df["end_of_program_hour"] <= 22), 1, 0)
            df["ends_in_primetime"] = np.where((df["end_of_program_hour"] >= 20) & (df["end_of_program_hour"] <= 22), 1, 0)
            df["starts_in_primetime"] = np.where((df["start_of_program_hour"] >= 20) & (df["start_of_program_hour"] <= 22), 1, 0)

            # Does the show have commercials?
            df["has_commercials"] = np.where(df["channel"].isin(["EEN", "CANVAS", "KETNET", "LA UNE"]), 0, 1)

            # Delta of sunrise and sunset
            df["sunrise_delta_start"] = df["start_of_program_hour"] - df["sunrise_time"].dt.hour
            df["sunrise_delta_end"] = df["end_of_program_hour"] - df["sunrise_time"].dt.hour
            df["sunset_delta_start"] = df["sunset_time"].dt.hour - df["start_of_program_hour"]
            df["sunset_delta_end"] = df["sunset_time"].dt.hour - df["end_of_program_hour"]

            # Convert some int to boolean features
            boolean_features = ["covid_19", "lockdown_1", "lockdown_2", "in_primetime", "ends_in_primetime", "starts_in_primetime", "has_commercials"]
            df[boolean_features] = df[boolean_features].astype(bool)

            return df


        except Exception as e:
            error_message = f"Error creating new features: {e}"
            logger.error(error_message)
            raise DataProcessingError(error_message) from e

    def select_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Select and order features from the data.

        Parameters
        ----------
        data : pandas.DataFrame
            The data to select features from

        Returns
        -------
        pandas.DataFrame
            The data with selected features
        """

        return data[self.FEATURES_LIST]