import pandas as pd


def save_as_csv(df: pd.DataFrame, csv_name: str):
    """
    Saves a pandas DataFrame to a CSV file.

    Args:
        df: The pandas DataFrame to save.
        csv_name: The name of the CSV file to create (including the .csv extension).
    """
    try:
        df.to_csv(csv_name, index=False)
        print(f"DataFrame successfully saved to '{csv_name}'")
    except Exception as e:
        print(f"Error saving DataFrame to CSV: {e}")
