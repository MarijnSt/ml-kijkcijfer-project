import requests
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
                "show": record.get("description"),
                "channel": record.get("channel"),
                "date": record.get("dateDiff"),
                "start": record.get("startTime"),
                "duration": record.get("rLength"),
                "viewers": record.get("rateInK"),
            }
            processed_records.append(processed_record)

        return processed_records
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {date}: {e}")
        return None

def correct_start_times(ratings_df):
    """
    Correct the dates of the ratings data.
    Some records have a starting time of 24:xx:xx or 25:xx:xx with the wrong date. They should get moved to the next day.

    Parameters:
    ----------
    ratings_df: pandas.DataFrame
        The ratings data in a DataFrame

    Returns:
    -------
    ratings_df_corrected: pandas.DataFrame
        The corrected ratings data in a DataFrame

    Example:
    -------
    >>> ratings_df_corrected = correct_start_times(ratings_df)
    >>> ratings_df_corrected.head()
    """
    # Create a copy to avoid modifying the original during iteration
    ratings_df_corrected = ratings_df.copy()

    # Get indices of faulty records
    faulty_indices = ratings_df[
        ratings_df["start"].str.startswith("24:") | 
        ratings_df["start"].str.startswith("25:")
    ].index

    print(f"Found {len(faulty_indices)} faulty 'start' records to correct")

    # Process each faulty record individually
    for idx in faulty_indices:
        start_time = ratings_df.loc[idx, "start"]
        original_date = ratings_df.loc[idx, "date"]
        
        if start_time.startswith("24:"):
            # Move to next day and convert 24:xx:xx to 00:xx:xx
            new_date = pd.to_datetime(original_date) + pd.Timedelta(days=1)
            new_start_time = start_time.replace("24:", "00:", 1)
            print(f"Record {idx}: {original_date} {start_time} → {new_date.strftime('%Y-%m-%d')} {new_start_time}")
            
        elif start_time.startswith("25:"):
            # Move to next day and convert 25:xx:xx to 01:xx:xx
            new_date = pd.to_datetime(original_date) + pd.Timedelta(days=1)
            new_start_time = start_time.replace("25:", "01:", 1)
            print(f"Record {idx}: {original_date} {start_time} → {new_date.strftime('%Y-%m-%d')} {new_start_time}")
        
        # Update the corrected dataframe
        ratings_df_corrected.loc[idx, "date"] = new_date
        ratings_df_corrected.loc[idx, "start"] = new_start_time

    print(f"\nCorrection complete! Updated {len(faulty_indices)} 'start' records.")

    return ratings_df_corrected

def normalize_channel_names(ratings_df):
    """
    Channel names have changed over the years. This function normalizes the channel names.

    Parameters:
    ----------
    ratings_df: pandas.DataFrame
        The ratings data in a DataFrame

    Returns:
    -------
    df: pandas.DataFrame
        The normalized ratings data in a DataFrame
    """
    # Create a copy of df
    df = ratings_df.copy()

    # Normalize the channel names
    df.loc[df["channel"].isin(["EEN", "VRT 1"]), "channel"] = "EEN"
    df.loc[df["channel"].isin(["Canvas", "CANVAS", "VRT CANVAS"]), "channel"] = "CANVAS"
    df.loc[df["channel"].isin(["KETNET", "OP 12"]), "channel"] = "KETNET"
    df.loc[df["channel"].isin(["VIER", "PLAY4"]), "channel"] = "PLAY4"
    df.loc[df["channel"].isin(["VIJF", "PLAY5"]), "channel"] = "PLAY5"
    df.loc[df["channel"].isin(["ZES", "PLAY6"]), "channel"] = "PLAY6"
    df.loc[df["channel"].isin(["Q2", "VTM2"]), "channel"] = "VTM2"
    df.loc[df["channel"].isin(["VITAYA", "VTM3"]), "channel"] = "VTM3"
    df.loc[df["channel"].isin(["CAZ", "VTM4"]), "channel"] = "VTM4"
    df.loc[df["channel"].isin(["EEN,VTM,PLAY4", "EEN, VTM, PLAY", "VRT 1/VTM/Play4"]), "channel"] = "EEN"
    df.loc[df["channel"].isin(["ELEVEN PRO LEAGUE 1 NL", "DAZN PRO LEAGUE 1 (NL)"]), "channel"] = "PRO LEAGUE 1"
    
    return df

def format_data(ratings_df):
    """
    Format the columns of the ratings dataframe.

    Parameters:
    ----------
    ratings_df: pandas.DataFrame
        The ratings data in a DataFrame

    Returns:
    -------
    df: pandas.DataFrame
        The formatted ratings data in a DataFrame
    """
    # Create a copy of df
    df = ratings_df.copy()

    # Convert 'date' to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Fix faulty 'start' values
    df = correct_start_times(df)

    # Convert 'start' to time and combine with 'date' to create proper datetime
    start_times = pd.to_datetime(df["start"], format='%H:%M:%S').dt.time
    df["start"] = [pd.Timestamp.combine(d, t) for d, t in zip(df['date'], start_times)]

    # Convert 'duration' to timedelta
    df["duration"] = pd.to_timedelta(df["duration"])

    # Replace 'kijkers' data dots and commas
    df["viewers"] = df["viewers"].str.replace(".", "").str.replace(",", ".")

    # Convert 'kijkers' to numeric (errors converted to NaN)
    df["viewers"] = pd.to_numeric(df["viewers"], errors='coerce')

    # Drop rows with faulty 'kijkers' data (NaN)
    df = df.dropna(subset=['viewers'])

    # Convert 'kijkers' to int
    df["viewers"] = df["viewers"].astype(int)

    return df

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
        end_date = datetime.now() - timedelta(days=3)
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
        
        # Format data
        df = format_data(df)

        # Drop rows with missing values
        df = df.dropna()
        
        print(f"\nTotal records collected: {len(df)}")
        return df
    else:
        print("No data collected")
        return pd.DataFrame()

def create_ratings_parquet():
    """
    Create a parquet file from the ratings data.
    """

    file_name = "ratings_data_test.parquet"

    print(f"Creating {file_name}...")
    df = get_ratings_data("2017-12-31", "2018-1-1")
    df.to_parquet(file_name)

    print(f"{file_name} created at project root")


if __name__ == "__main__":
    create_ratings_parquet()