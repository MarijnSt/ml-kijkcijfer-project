import pandas as pd
import logging
from pathlib import Path
from typing import Union

from ..utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)

def save_parquet(
    df: pd.DataFrame,
    output_path: Union[str, Path],
    **kwargs
) -> Path:
    """
    Save a pandas DataFrame to a parquet file.

    Parameters:
    ----------
    df: pandas.DataFrame
        The DataFrame to save
    output_path: Union[str, Path]
        The path to save the parquet file
    **kwargs: dict
        Additional arguments passed to pandas DataFrame.to_parquet method

    Returns:
    -------
    Path
        The path to the saved parquet file

    Raises:
    -------
    DataProcessingError
        If the file operation fails
    """

    try:
        output_path = Path(output_path)
        logger.info(f"Saving DataFrame to parquet file: {output_path}")

        if df.empty:
            logger.warning("No data to save to parquet file")
            return output_path

        df.to_parquet(output_path, **kwargs)

        # Log file size
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        logger.info(f"Successfully saved {len(df)} records to {output_path} ({file_size:.1f} MB)")

        return output_path
    
    except Exception as e:
        error_message = f"Error saving DataFrame to parquet file: {e}"
        logger.error(error_message)
        raise DataProcessingError(error_message) from e