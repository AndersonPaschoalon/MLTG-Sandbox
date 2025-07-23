import pandas as pd
from pandas import DataFrame

from trace_analyzer.core.state import get_env, get_mem
from trace_analyzer.registers.analysis import AnalysisRegistry

env = get_env()
mem = get_mem()


def _plot_this(target, target_list):
    """
    Determine whether the given target should be plotted based on an optional filter list.

    Args:
        target (str): The target identifier (e.g., a trace label or experiment run name).
        target_list (list[str]): Optional list of targets to include.

    Returns:
        bool: True if the target should be included, False otherwise.

    Logic:
    - If `target_list` is empty, include all targets.
    - Otherwise, include only those explicitly listed.
    """
    return not target_list or target in target_list


def prepare_distribution_data(
    df_map: dict[str, DataFrame],
    time_column: str,
    max_time: float,
    target_list: list[str],
):
    """
    Prepare filtered data for distribution plotting.

    This function filters the DataFrame map (`df_map`)by:
    - Restricting data to targets included in `target_list`.
    - Truncating data by the shared maximum time (`max_time`).

    It returns:
    - A dictionary of filtered DataFrames (`filtered_df_map`), ready for plotting.
    - A list of target names that are actually included in the plot (`compared_targets`).

    Parameters:
    ----------
    df_map: dict[str, pd.DataFrame]
        Dictionary mapping target names to DataFrames containing the data to be filtered.
    time_column: str
        The name of the column in the DataFrames that contains time values.
    max_time: float
        The maximum time value to filter the DataFrames by.
    target_list : list of str
        List of target names to include in the analysis.
        If empty, all targets in `df_map` are considered.

    Returns:
    -------
    filtered_df_map : dict[str, pd.DataFrame]
        Dictionary mapping target names to filtered DataFrames, each limited
        by `mem.inter_min_time_max`.

    compared_targets : list of str
        List of target names that were included in the filtering process,
        useful for tracking which targets are compared in the plot.

    Example:
    --------
    >>> filtered_map, targets = prepare_distribution_data(df_map, "time", max_time, ["orig", "swing"])
    >>> plot_pdf(filtered_map, ...)
    """
    # Filter df_map by time and target list
    filtered_df_map = {}
    for target, df in df_map.items():
        if not _plot_this(target, target_list):
            continue
        filtered_df = df[df[time_column] <= max_time]
        filtered_df_map[target] = filtered_df
    # Generate filename based on included targets
    compared_targets = list(filtered_df_map.keys())
    return filtered_df_map, compared_targets


def filter_df_map_by_target(df_map: dict[str, DataFrame], target_list: list[str]):
    """
    Filter the DataFrame map by the target list.

    This function filters the DataFrame map (`mem.inter_df_map`) to include only those targets
    that are specified in `target_list`. If `target_list` is empty, all targets are included.

    Returns:
        dict[str, DataFrame]: Filtered DataFrame map.
    """
    filtered_df_map = {}
    for target, df in df_map.items():
        if _plot_this(target, target_list):
            filtered_df_map[target] = df
    return filtered_df_map


def load_stored_analysis_data(target_list=None):

    def _load_data_with_min_time(data_target, target_list, time_column="time"):
        """
        Load CSVs for data targets and compute the minimal max time across DataFrames.

        Returns:
            data_map (dict): target → DataFrame
            min_time_max (float): smallest of all max times
        """
        data_map = {}
        min_time_max = None

        for file, target in data_target:
            if _plot_this(target, target_list):
                df = pd.read_csv(file)
                data_map[target] = df
                max_time = df[time_column].max()
                if min_time_max is None or max_time < min_time_max:
                    min_time_max = max_time
        return data_map, min_time_max

    def _load_data_map(data_target, target_list):
        """
        Load CSVs for data targets into a simple target → DataFrame map.

        Returns:
            data_map (dict): target → DataFrame
        """
        data_map = {}
        for file, target in data_target:
            if _plot_this(target, target_list):
                df = pd.read_csv(file)
                data_map[target] = df
        return data_map

    for analysis_name, analysis_def in AnalysisRegistry.get_all().items():
        if analysis_def["requires_min_time"]:
            df_map, min_time = _load_data_with_min_time(
                getattr(mem, analysis_def["mem_attribute"]), target_list, "time"
            )
            print(
                f" -  setting {analysis_name}_df_map and {analysis_name}_min_time_max for {analysis_name}"
            )
            setattr(mem, f"{analysis_name}_df_map", df_map)
            setattr(mem, f"{analysis_name}_min_time_max", min_time)
        else:
            df_map = _load_data_map(
                getattr(mem, analysis_def["mem_attribute"]), target_list
            )
            print(f" -  setting {analysis_name}_df_map for {analysis_name}")
            setattr(mem, f"{analysis_name}_df_map", df_map)
