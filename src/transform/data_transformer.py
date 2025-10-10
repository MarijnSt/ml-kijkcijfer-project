import pandas as pd
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
    - TODO: data formatting, ???
    """

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


        except Exception as e:
            error_message = f"Error creating new features: {e}"
            logger.error(error_message)
            raise DataProcessingError(error_message) from e