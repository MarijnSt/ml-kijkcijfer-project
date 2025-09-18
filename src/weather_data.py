import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

def get_historical_weather_data(start_date, end_date):
    """
    Get historical weather data from the Open-Meteo API.
    The location is fixed to Ukkel.

    Parameters:
    ----------
    start_date: str
        The start date of the weather data to get (format: YYYY-MM-DD).
    end_date: str
        The end date of the weather data to get (format: YYYY-MM-DD).

    Returns:
    -------
    pandas.DataFrame
        The weather data.
    """

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 50.8023, # Ukkel
        "longitude": 4.3394,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["weather_code", "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max"],
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    # print(f"Elevation: {response.Elevation()} m asl")
    # print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_mean = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_max = daily.Variables(2).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(3).ValuesAsNumpy()
    daily_sunrise = daily.Variables(4).ValuesInt64AsNumpy()
    daily_sunset = daily.Variables(5).ValuesInt64AsNumpy()
    daily_daylight_duration = daily.Variables(6).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(7).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(8).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(9).ValuesAsNumpy()
    daily_snowfall_sum = daily.Variables(10).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(11).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(12).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(13).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["weather_code"] = daily_weather_code
    daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["sunrise"] = daily_sunrise
    daily_data["sunrise_time"] = pd.to_datetime(daily_sunrise, unit='s')
    daily_data["sunset"] = daily_sunset
    daily_data["sunset_time"] = pd.to_datetime(daily_sunset, unit='s')
    daily_data["daylight_duration"] = daily_daylight_duration
    daily_data["sunshine_duration"] = daily_sunshine_duration
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["rain_sum"] = daily_rain_sum
    daily_data["snowfall_sum"] = daily_snowfall_sum
    daily_data["precipitation_hours"] = daily_precipitation_hours
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
    daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max

    return pd.DataFrame(data = daily_data)