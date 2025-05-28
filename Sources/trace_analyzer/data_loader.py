import pandas as pd

from commons.naming.analysis_data_name_formatter import (
    AnalysisDataNameFormatter as ADNF,
)
from trace_analyzer.core import get_env, get_mem, load_env

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


# TODO: passar "time" como parametro
def prepare_distribution_data(target_list: list[str]):
    """
    Prepare filtered data for distribution plotting.

    This function filters the global inter-arrival DataFrame map (`mem.inter_df_map`)
    by:
    - Restricting data to targets included in `target_list`.
    - Truncating data by the shared maximum time (`mem.inter_min_time_max`).

    It returns:
    - A dictionary of filtered DataFrames (`filtered_df_map`), ready for plotting.
    - A list of target names that are actually included in the plot (`compared_targets`).

    Parameters:
    ----------
    target_list : list of str
        List of target names to include in the analysis.
        If empty, all targets in `mem.inter_df_map` are considered.

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
    >>> filtered_map, targets = prepare_distribution_data(["orig", "swing"])
    >>> plot_pdf(filtered_map, ...)
    """
    # Filter df_map by time and target list
    filtered_df_map = {}
    for target, df in mem.inter_df_map.items():
        if not _plot_this(target, target_list):
            continue
        filtered_df = df[df["time"] <= mem.inter_min_time_max]
        filtered_df_map[target] = filtered_df
    # Generate filename based on included targets
    compared_targets = list(filtered_df_map.keys())
    return filtered_df_map, compared_targets


def load_stored_analysis_data(target_list=None):
    """
    Load post-analysis data from CSVs, prepare in-memory DataFrames and compute min time ranges.

    Data types loaded:
    - Inter-arrival Data: mem.inter_df_map + mem.inter_min_time_max
    - Bandwidth/PPS/FPS Data: mem.bw_df_map + mem.bw_min_time_max
    - Burst Durations: mem.bdurations_df_map
    - Burst Intervals: mem.bintervals_df_map
    - Burst Sizes: mem.bsizes_df_map

    Args:
        target_list (list[str], optional): Filter for which targets to load. If empty, load all.
    """

    # utility 01
    def _load_data_with_min_time(data_target, target_list):
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
                max_time = df["time"].max()
                if min_time_max is None or max_time < min_time_max:
                    min_time_max = max_time
        return data_map, min_time_max

    # utility 02
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

    if target_list is None:
        target_list = []

    load_env()

    # Data that needs min time tracking
    mem.inter_df_map, mem.inter_min_time_max = _load_data_with_min_time(
        mem.interdata_target, target_list
    )
    mem.bw_df_map, mem.bw_min_time_max = _load_data_with_min_time(
        mem.bwdata_target, target_list
    )

    # Simple data maps
    mem.bdurations_df_map = _load_data_map(mem.burstdurdata_target, target_list)
    mem.bintervals_df_map = _load_data_map(mem.burstinterdata_target, target_list)
    mem.bsizes_df_map = _load_data_map(mem.burstsizesdata_target, target_list)
    mem.wavelet_df_map = _load_data_map(mem.waveletdata_target, target_list)

    print("load_analysis_data done")
