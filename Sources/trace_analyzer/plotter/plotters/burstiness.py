import logging

import matplotlib.cm as cm

import trace_analyzer.core.data_loader as data_loader
import trace_analyzer.plotter.functions.plot_functions as plot_functions
from commons.logger.logger import Logger
from trace_analyzer.core.state import get_env, get_mem

env = get_env()
mem = get_mem()


def plot_burst_duration_violin(target_list=None):
    """
    Plot violin distribution of burst durations for each target.
    """
    df_map = data_loader.filter_df_map_by_target(
        mem.burst_durations_df_map, target_list
    )
    filename = mem.pnf.mkname("violin-burst-duration", list(df_map.keys()))
    plot_functions.plot_distribution_plot(
        df_map=df_map,
        column="burst_duration",
        title="Violin Plot of Burst Durations",
        xlabel="Target",
        ylabel="Burst Duration (s)",
        save_path_base=filename,
        plot_kind="violin",
        log_y=True,
    )


def plot_inter_burst_interval_cdf(target_list=None):
    """
    Plot CDF of inter-burst intervals for each target.
    """
    df_map = data_loader.filter_df_map_by_target(
        mem.burst_intervals_df_map, target_list
    )
    filename = mem.pnf.mkname("burst_interval_cdf", list(df_map.keys()))
    plot_functions.plot_cdf(
        df_map=df_map,
        column="burst_interval",
        xlabel="Inter-Burst Interval (s)",
        title="Inter-Burst Interval Distribution (CDF)",
        save_path_base=filename,
        log_scale=True,
    )


def plot_burst_size_violin(target_list=None):
    """
    Plot violin distribution of burst sizes for each target.
    """
    df_map = data_loader.filter_df_map_by_target(mem.burst_sizes_df_map, target_list)
    filename = mem.pnf.mkname("violin-burst-size", list(df_map.keys()))
    plot_functions.plot_distribution_plot(
        df_map=df_map,
        column="burst_size",
        title="Violin Plot of Burst Sizes",
        xlabel="Target",
        ylabel="Burst Size (packets)",
        save_path_base=filename,
        plot_kind="violin",
        log_y=True,
    )
