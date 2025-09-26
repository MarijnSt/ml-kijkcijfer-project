"""Ratings data processing utilities."""

import pandas as pd
import logging
from typing import List, Dict, Any

from ..utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)


class RatingsTransformer:
    """
    Processes and cleans ratings data.
    
    This class handles all data processing operations for ratings data,
    including time corrections, channel normalization, and data formatting.
    """

    # Channel mappings as class variable so it's not recreated every time the normalize_channel_names method is called
    CHANNEL_MAPPINGS = {
        "EEN": ["EEN", "VRT 1", "EEN,VTM,PLAY4", "EEN, VTM, PLAY", "VRT 1/VTM/Play4"],
        "CANVAS": ["Canvas", "CANVAS", "VRT CANVAS"],
        "KETNET": ["KETNET", "OP 12"],
        "PLAY4": ["VIER", "PLAY4"],
        "PLAY5": ["VIJF", "PLAY5"],
        "PLAY6": ["ZES", "PLAY6"],
        "VTM2": ["Q2", "VTM2"],
        "VTM3": ["VITAYA", "VTM3"],
        "VTM4": ["CAZ", "VTM4"],
        "PRO LEAGUE 1": ["ELEVEN PRO LEAGUE 1 NL", "DAZN PRO LEAGUE 1 (NL)"]
    }
    
    def correct_start_times(self, ratings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Correct the dates of the ratings data.
        
        Some records have a starting time of 24:xx:xx or 25:xx:xx with the wrong date. 
        They should get moved to the next day.

        Parameters
        ----------
        ratings_df : pandas.DataFrame
            The ratings data in a DataFrame

        Returns
        -------
        pandas.DataFrame
            The corrected ratings data in a DataFrame

        Raises
        ------
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

            logger.info(f"Correction complete! Updated {corrected_count} 'start' records.")
            return ratings_df_corrected
        
        except Exception as e:
            error_message = f"Error correcting start times: {e}"
            logger.error(error_message)
            raise DataProcessingError(error_message) from e

    def normalize_channel_names(self, ratings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Channel names have changed over the years. 
        This function normalizes the channel names.

        Parameters
        ----------
        ratings_df : pandas.DataFrame
            The ratings data in a DataFrame

        Returns
        -------
        pandas.DataFrame
            The normalized ratings data in a DataFrame

        Raises
        ------
        DataProcessingError
            If the data processing fails
        """
        try:
            # Create a copy of df
            df = ratings_df.copy()
            
            normalization_count = 0
            for normalized_name, variants in self.CHANNEL_MAPPINGS.items():
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

    def format_data(self, ratings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Format the columns of the ratings dataframe.

        Parameters
        ----------
        ratings_df : pandas.DataFrame
            The ratings data in a DataFrame

        Returns
        -------
        pandas.DataFrame
            The formatted ratings data in a DataFrame

        Raises
        ------
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
            df = self.correct_start_times(df)

            # Convert 'start' to datetime and convert errors to NaT
            df["start"] = pd.to_datetime(df["start"], format='%H:%M:%S', errors='coerce')
            invalid_start_count = len(df[df["start"].isna()])
            if invalid_start_count > 0:
                logger.warning(f"Found {invalid_start_count} invalid 'start' values. Will be dropped.")

            # Drop rows with NaT 'start' values
            df = df.dropna(subset=['start'])

            # Combine 'start' with 'date' to create proper datetime
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
            df = self.normalize_channel_names(df)

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