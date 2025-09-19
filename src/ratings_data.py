import requests_cache
from retry_requests import retry
import pandas as pd
from datetime import datetime, timedelta
import time

def get_cim_tv_data(date, session):
    """
    Fetch data from CIM TV API and convert it to a pandas DataFrame.

    Parameters:
    ----------
    date: str
        The date in format YYYY-M-D
    session: requests.Session
        The cached session to use for requests

    Returns:
    -------
    list or None
        List of dictionaries (records) or None if error
    """
    
    # Construct the API URL
    api_url = f"https://api.cim.be/api/cim_tv_public_results_daily_views?dateDiff={date}&reportType=north"

    try:
        # Make the API request using the provided session
        response = session.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Get the ratings data from the response
        ratings_data = data['hydra:member']

        if not ratings_data:
            return None

        # Process and clean the data
        processed_records = []
        for record in ratings_data:
            # Keep only relevant columns and rename them
            processed_record = {
                "programma": record.get("description"),
                "zender": record.get("channel"),
                "datum": record.get("dateDiff"),
                "start": record.get("startTime"),
                "duur": record.get("rLength"),
                "kijkers": record.get("rateInK"),
            }
            processed_records.append(processed_record)

        return processed_records
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {date}: {e}")
        return None

def get_ratings_data(start_date="2016-10-1", end_date="latest"):
    """
    Fetch ratings data from CIM TV API for a given date range.

    Parameters:
    ----------
    start_date: str
        The start date of the date range (format: YYYY-MM-DD)
    end_date: str
        The end date of the date range (format: YYYY-MM-DD)
        default: "latest" (two days ago is the latest possible date)

    Returns:
    -------
    df: pandas.DataFrame
        The ratings data in DataFrame format
    """
    # Setup request session with cache and retry on error (once for all requests)
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)

    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date == "latest":
        end_date = datetime.now() - timedelta(days=2)
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Initialize list to collect all records
    all_records = []

    # Loop through dates in the range
    current_date = start_date
    while current_date <= end_date:
        try:
            # Format date back to string (API format: YYYY-M-D)
            date_str = current_date.strftime("%Y-%-m-%-d")
            print(f"Fetching data for: {date_str}")

            # Get data for current date using the shared session
            daily_records = get_cim_tv_data(date_str, retry_session)

            # Add to list
            if daily_records:
                all_records.extend(daily_records)
                print(f"✓ Added {len(daily_records)} records")
            else:
                print(f"✗ No data for date: {date_str}")

            # Add a delay between requests to avoid rate limiting
            time.sleep(1)
            
            # Move to next day
            current_date += timedelta(days=1)

        except Exception as e:
            print(f"Error processing date {date_str}: {str(e)}")
            time.sleep(5)
            continue
    
    # Create DataFrame once at the end
    if all_records:
        df = pd.DataFrame(all_records)
        print(f"\nTotal records collected: {len(df)}")
        return df
    else:
        print("No data collected")
        return pd.DataFrame()

# Usage example:
# df = get_ratings_data("2024-01-01", "2024-01-07")