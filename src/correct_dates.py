import pandas as pd

def correct_dates(ratings_df):
    """
    Correct the dates of the ratings data.
    Some records have a starting time of 24:xx:xx, 25:xx:xx and 00:xx:xx with the wrong date. They should get moved to the next day.

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
    >>> ratings_df_corrected = correct_dates(ratings_df)
    >>> ratings_df_corrected.head()
    """
    # Create a copy to avoid modifying the original during iteration
    ratings_df_corrected = ratings_df.copy()

    # Get indices of faulty records
    faulty_indices = ratings_df[
        ratings_df["start"].str.startswith("24:") | 
        ratings_df["start"].str.startswith("25:") | 
        ratings_df["start"].str.startswith("00:")
    ].index

    print(f"Found {len(faulty_indices)} faulty records to correct")

    # Process each faulty record individually
    for idx in faulty_indices:
        start_time = ratings_df.loc[idx, "start"]
        original_date = ratings_df.loc[idx, "datum"]
        
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
            
        elif start_time.startswith("00:"):
            # Move to next day, keep 00:xx:xx as is
            new_date = pd.to_datetime(original_date) + pd.Timedelta(days=1)
            new_start_time = start_time  # Keep as 00:xx:xx
            print(f"Record {idx}: {original_date} {start_time} → {new_date.strftime('%Y-%m-%d')} {new_start_time}")
        
        # Update the corrected dataframe
        ratings_df_corrected.loc[idx, "datum"] = new_date
        ratings_df_corrected.loc[idx, "start"] = new_start_time

    print(f"\nCorrection complete! Updated {len(faulty_indices)} records.")

    return ratings_df_corrected