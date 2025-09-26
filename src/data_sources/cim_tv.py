"""CIM TV API client."""

from typing import Optional, List, Dict, Any
from datetime import datetime
import time
import logging

from ..config.settings import config
from ..utils.exceptions import APIError, ValidationError
from ..utils.session_manager import SessionManager


logger = logging.getLogger(__name__)


class CIMTVClient:
    """
    Client for CIM TV API.
    
    This class handles all interactions with the CIM TV API, including
    data fetching, error handling, and response processing.
    """
    
    def __init__(self):
        """Initialize CIM TV client with configuration."""
        self.config = config.cim_tv
        self.session_manager = SessionManager(self.config)
    
    def get_data(self, date: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch data from CIM TV API for a specific date.

        Parameters
        ----------
        date : str
            The date in format YYYY-M-D

        Returns
        -------
        list or None
            List of dictionaries (records) or None if no data

        Raises
        ------
        APIError
            If the API request fails
        ValidationError
            If the date format is invalid
        """
        # Validate the date format
        try:
            datetime.strptime(date, config.data.api_date_format)
        except ValueError:
            raise ValidationError(f"Invalid date format: {date}. Expected format: YYYY-M-D")

        # Construct the API URL
        api_url = f"{self.config.base_url}?dateDiff={date}&reportType=north"
        logger.info(f"Fetching data from API for date: {date}")

        try:
            # Make the API request
            response = self.session_manager.session.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            # Get the ratings data from the response
            ratings_data = data.get('hydra:member', [])

            if not ratings_data:
                logger.warning(f"No data found for date: {date}")
                return None

            # Process the data
            processed_records = []
            for record in ratings_data:
                try:
                    processed_record = {
                        "show": record.get("description"),
                        "channel": record.get("channel"),
                        "date": record.get("dateDiff"),
                        "start": record.get("startTime"),
                        "duration": record.get("rLength"),
                        "viewers": record.get("rateInK"),
                    }
                    processed_records.append(processed_record)
                except Exception as e:
                    logger.error(f"Error processing record for date: {date}: {e}")
                    continue

            logger.info(f"Successfully processed {len(processed_records)} records for date: {date}")
            return processed_records
        
        except Exception as e:
            error_message = f"Error fetching data for date: {date}: {e}"
            logger.error(error_message)
            raise APIError(error_message) from e