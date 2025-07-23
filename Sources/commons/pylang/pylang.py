import json
import os
from typing import Any

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


def set_json_param(filepath: str, param: str, new_value: Any) -> None:
    """
    Sets a top-level parameter in a JSON file with auto type detection.

    Args:
        json_file (str): Path to the JSON file.
        param (str): Parameter to update (must exist at the top level).
        new_value (str): New value to set (will be auto-cast to correct type).

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        KeyError: If the parameter is not found in the JSON.
        ValueError: If the new value cannot be interpreted as a supported type.
    """
    try:
        with open(filepath, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] File not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"[ERROR] Failed to parse JSON in {filepath}: {e}")
    if param not in config:
        raise KeyError(f"[ERROR] Parameter '{param}' not found in JSON file.")
    new_type = type(new_value)
    config[param] = new_value
    try:
        with open(filepath, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        raise IOError(f"[ERROR] Failed to write JSON file {filepath}: {e}")
