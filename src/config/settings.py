"""Configuration settings for the ML Kijkcijfer project."""

# API Settings
CIM_TV_API = {
    "base_url": "https://api.cim.be/api/cim_tv_public_results_daily_views",
    "retry_count": 5,
    "backoff_factor": 0.2,
    "request_delay": 1.0,
    "error_delay": 5.0
}

WEATHER_API = {
    "base_url": "https://archive-api.open-meteo.com/v1/archive",
    "retry_count": 5,
    "backoff_factor": 0.2,
    "request_delay": 1.0,
    "error_delay": 5.0
}

# Cache Settings
CACHE_DIR = ".cache"
CACHE_EXPIRE_AFTER = -1  # Never expire

# Data Settings
DEFAULT_START_DATE = "2016-10-1"
LATEST_OFFSET_DAYS = 2
DATE_FORMAT = "%Y-%m-%d"
API_DATE_FORMAT = "%Y-%-m-%-d"

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FILE = "ratings_data.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Weather Settings
WEATHER_LOCATION = {
    "latitude": 50.8023,  # Ukkel
    "longitude": 4.3394
}

WEATHER_VARIABLES = [
    "weather_code", "temperature_2m_mean", "temperature_2m_max", 
    "temperature_2m_min", "sunrise", "sunset", "daylight_duration", 
    "sunshine_duration", "precipitation_sum", "rain_sum", 
    "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", 
    "wind_gusts_10m_max"
]