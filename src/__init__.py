# TODO: add imports for config (create config class)

from .config import (
    setup_logging
)

from .data_sources import (
    CIMTVClient,
    WeatherClient
)
from .extract import (
    fetch_ratings_data,
    fetch_weather_data
)
from .load import (
    save_parquet
)
from .transform import (
    RatingsTransformer,
    WeatherTransformer
)
from .utils import (
    DataError,
    APIError, 
    DataProcessingError,
    ValidationError,
    SessionManager
)

__all__ = [
    # Config
    "setup_logging",

    # Data sources
    "CIMTVClient", 
    "WeatherClient",

    # Extract
    "fetch_ratings_data",
    "fetch_weather_data",
    
    # Load
    "save_parquet",

    # Transform
    "RatingsTransformer",
    "WeatherTransformer",
    
    # Utils
    "DataError",
    "APIError", 
    "DataProcessingError",
    "ValidationError",
    "SessionManager",
]