import argparse
import logging
import math
import os
import sys
import traceback

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import gaussian_kde

import commons.pylang.pylang as pl
import trace_analyzer.analyzer as analyzer
import trace_analyzer.core_state as core_state
import trace_analyzer.data_loader as data_loader
import trace_analyzer.metrics_estimator as metrics_estimator
import trace_analyzer.plot_functions as plot_functions
from commons.config.experiment_config import ExperimentConfig
from commons.connectors.alchemy_connector import AlchemyConnector
from commons.enviroment.env import Env
from commons.enviroment.memory_store import MemoryStore
from commons.logger.logger import Logger
from commons.naming.analysis_data_name_formatter import (
    AnalysisDataNameFormatter as ADNF,
)
from commons.naming.plot_name_formatter import PlotNameFormatter as PNF
from commons.naming.raw_data_name_formatter import RawDataNameFormatter as RDNF
from commons.pylang.os_utils import OSUtils as osutils
from trace_analyzer.core_state import get_env, get_mem, load_env
from trace_analyzer.sniffer_wrapper import SnifferWrapper

env = get_env()
mem = get_mem()

# TODO: Remover, adicionar ao main.py
Logger.initialize(
    "./Logs/trace_analyser.log", level_log=logging.DEBUG, level_console=logging.DEBUG
)


def plot_violin_interarrival(target_list=None):
    """
    Plot violin distribution of inter-arrival times for each target.

    Filters data up to mem.interarrival_min_time_max and optionally by target_list.
    """
    filtered_df_map, compared_targets = data_loader.prepare_distribution_data(
        df_map=mem.interarrival_df_map,
        time_column="time",
        max_time=mem.interarrival_min_time_max,
        target_list=target_list,
    )
    filename = mem.pnf.mkname("violin-interarrival", compared_targets)
    plot_functions.plot_distribution_plot(
        df_map=filtered_df_map,
        column="inter_arrival",
        title="Violin Plot of Inter-Arrival Times",
        xlabel="Target",
        ylabel="Inter-Arrival Time (s)",
        save_path_base=filename,
        plot_kind="violin",
        log_y=True,
    )


def plot_violin_pkt(target_list=None):
    """
    Plot violin distribution of packet sizes for each target.

    Filters data up to mem.interarrival_min_time_max and optionally by target_list.
    """
    filtered_df_map, compared_targets = data_loader.prepare_distribution_data(
        df_map=mem.interarrival_df_map,
        time_column="time",
        max_time=mem.interarrival_min_time_max,
        target_list=target_list,
    )
    filename = mem.pnf.mkname("violin-pkt", compared_targets)

    plot_functions.plot_distribution_plot(
        df_map=filtered_df_map,
        column="pkt_size",
        title="Violin Plot of Packet Sizes",
        xlabel="Target",
        ylabel="Packet Size (bytes)",
        save_path_base=filename,
        plot_kind="violin",
        log_y=True,
    )


def plot_box_interarrival(target_list=None):
    """
    Plot boxplot distribution of inter-arrival times for each target.

    Filters data up to mem.interarrival_min_time_max and optionally by target_list.
    """
    filtered_df_map, compared_targets = data_loader.prepare_distribution_data(
        df_map=mem.interarrival_df_map,
        time_column="time",
        max_time=mem.interarrival_min_time_max,
        target_list=target_list,
    )
    filename = mem.pnf.mkname("box-interarrival", compared_targets)
    plot_functions.plot_distribution_plot(
        df_map=filtered_df_map,
        column="inter_arrival",
        title="Box Plot of Inter-Arrival Times",
        xlabel="Target",
        ylabel="Inter-Arrival Time (s)",
        save_path_base=filename,
        plot_kind="box",
        log_y=True,
    )


def plot_box_pkt(target_list=None):
    """
    Plot boxplot distribution of packet sizes for each target.

    Filters data up to mem.interarrival_min_time_max and optionally by target_list.
    """
    filtered_df_map, compared_targets = data_loader.prepare_distribution_data(
        df_map=mem.interarrival_df_map,
        time_column="time",
        max_time=mem.interarrival_min_time_max,
        target_list=target_list,
    )
    filename = mem.pnf.mkname("box-pkt", compared_targets)

    plot_functions.plot_distribution_plot(
        df_map=filtered_df_map,
        column="pkt_size",
        title="Box Plot of Packet Sizes",
        xlabel="Target",
        ylabel="Packet Size (bytes)",
        save_path_base=filename,
        plot_kind="box",
        log_y=True,
    )


def plot_interarrival_pdf(target_list=None):
    """
    Plot the PDF of inter-arrival times (log-log KDE).
    """
    df_map = data_loader.filter_df_map_by_target(mem.interarrival_df_map, target_list)
    targets = list(df_map.keys())

    filename = mem.pnf.mkname("pdf-interarrival", targets)
    plot_functions.plot_pdf(
        df_map=df_map,
        column="inter_arrival",
        title="PDF of Inter-Arrival Times (log-domain normalized)",
        xlabel="Inter-Arrival Time (s)",
        ylabel="Density",
        save_path_base=filename,
        log_x=True,
        log_y=False,
    )


def plot_interarrival_cdf(target_list=None):
    """
    Wrapper to plot the CDF of inter-arrival times using the generic plot_cdf().
    Filters targets if target_list is provided.
    """
    df_map = data_loader.filter_df_map_by_target(mem.interarrival_df_map, target_list)
    targets = list(df_map.keys())
    filename = mem.pnf.mkname("cdf-interarrival", targets)

    plot_functions.plot_cdf(
        df_map=df_map,
        column="inter_arrival",
        xlabel="Inter-Arrival Time (s)",
        title="CDF of Inter-Arrival Times",
        save_path_base=filename,
        log_scale=True,
    )


def plot_interarrival_by_index(target_list=None):
    """
    Plot inter-arrival time over packet index, per target.
    """
    df_map = data_loader.filter_df_map_by_target(mem.interarrival_df_map, target_list)

    # Ensure 'index' column exists
    for df in df_map.values():
        df.reset_index(drop=True, inplace=True)
        df["index"] = df.index

    targets = list(df_map.keys())
    filename = mem.pnf.mkname("interarrival_by_index", targets)

    plot_functions.plot_line(
        df_map=df_map,
        x_col="index",
        y_col="inter_arrival",
        xlabel="Packet Index",
        ylabel="Interarrival Time (s)",
        title="Interarrival Time by Packet Index",
        save_path_base=filename,
        log_y=True,
    )


def plot_bw_pps_fps_refactored(plot_type, target_list=None):
    """
    Plot bandwidth, packets/sec or flows/sec using preloaded mem.bw_pps_fps_df_map and mem.bw_pps_fps_min_time_max.
    """
    df_map = data_loader.filter_df_map_by_target(mem.bw_pps_fps_df_map, target_list)
    compared = list(df_map.keys())
    tmax = mem.bw_pps_fps_min_time_max

    metric_map = {
        "bandwidth": ("bandwidth", "bandwidth_average", "Bandwidth (bps)"),
        "packet_per_second": ("npackets", "npackets_average", "Packets per Second"),
        "flow_per_second": ("nflows", "nflows_average", "Flows per Second"),
    }
    if plot_type not in metric_map:
        raise ValueError(f"Unknown plot_type '{plot_type}'")

    raw_col, avg_col, y_label = metric_map[plot_type]
    save_path = mem.pnf.mkname(plot_type, compared)

    plot_functions.plot_timeseries(
        df_map=df_map,
        x_col="time",
        y_cols=[(raw_col, "raw", 1), (avg_col, "avg", 2.5)],
        title=f"{y_label} vs Time",
        xlabel="Time (s)",
        ylabel=y_label,
        save_path_base=save_path,
        time_max=tmax,
    )


def plot_pktsize_histogram(target_list=None):
    """
    Plot a separate packet size histogram for each target.
    """
    # if target_list:
    #    df_map = {k: v for k, v in mem.interarrival_df_map.items() if k in target_list}
    # else:
    #    df_map = mem.interarrival_df_map
    df_map = data_loader.filter_df_map_by_target(mem.interarrival_df_map, target_list)

    colors = cm.get_cmap("tab10")
    for i, (target, df) in enumerate(df_map.items()):
        df = df[df["time"] <= mem.bw_pps_fps_min_time_max]
        save_path = mem.pnf.mkname("histogram-pktsize", [target])
        color = colors(i % 10)
        plot_functions.plot_histogram(
            df=df,
            column="pkt_size",
            title=f"Packet Size Distribution — {target}",
            xlabel="Packet Size (bytes)",
            ylabel="Frequency",
            save_path=save_path,
            color=color,
        )


def plot_bandwidth_cdf(target_list=None):
    """
    Plot the CDF of bandwidth values for each target.
    Uses preloaded and truncated data from mem.bw_pps_fps_df_map and mem.bw_pps_fps_min_time_max.
    """
    truncated_map, compared_targets = data_loader.prepare_distribution_data(
        df_map=mem.bw_pps_fps_df_map,
        time_column="time",
        max_time=mem.bw_pps_fps_min_time_max,
        target_list=target_list,
    )

    save_path_base = mem.pnf.mkname("bandwidth_cdf", compared_targets)
    plot_functions.plot_cdf(
        df_map=truncated_map,
        column="bandwidth",
        xlabel="Bandwidth (bps)",
        title="Bandwidth Distribution (CDF)",
        save_path_base=save_path_base,
        log_scale=True,
    )


def plot_payload_size_cdf(target_list=None):
    """
    Plot the CDF of packet sizes for each target.
    Uses preloaded and truncated interarrival data from mem.interarrival_df_map and mem.interarrival_min_time_max.
    """
    truncated_map, compared_targets = data_loader.prepare_distribution_data(
        df_map=mem.interarrival_df_map,
        time_column="time",
        max_time=mem.interarrival_min_time_max,
        target_list=target_list,
    )
    save_path_base = mem.pnf.mkname("payload_size_cdf", compared_targets)
    plot_functions.plot_cdf(
        df_map=truncated_map,
        column="pkt_size",
        xlabel="Packet Size (Bytes)",
        title="Payload Size Distribution (CDF)",
        save_path_base=save_path_base,
        log_scale=True,
    )


def plot_packet_load_cdf(target_list=None):
    """
    Plot the CDF of packet load (packets per second) for each target.
    Uses preloaded and truncated data from mem.bw_pps_fps_df_map and mem.bw_pps_fps_min_time_max.
    """
    truncated_map, compared_targets = data_loader.prepare_distribution_data(
        df_map=mem.bw_pps_fps_df_map,
        time_column="time",
        max_time=mem.bw_pps_fps_min_time_max,
        target_list=target_list,
    )
    save_path_base = mem.pnf.mkname("packet_load_cdf", compared_targets)
    plot_functions.plot_cdf(
        df_map=truncated_map,
        column="npackets",
        xlabel="Packets per Second",
        title="Packet Load Distribution (CDF)",
        save_path_base=save_path_base,
        log_scale=True,
    )


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


def plot_wavelet_multiresolution_energy_analysis(target_list=None):
    """
    Plots Multiresolution Energy analysis!
    wavelet_df_map
    """
    df_map = data_loader.filter_df_map_by_target(mem.wavelet_df_map, target_list)
    filename = mem.pnf.mkname("wavelet-mea", list(df_map.keys()))
    plot_functions.plot_multiline_metric(
        df_map=df_map,
        x_column="scale",
        y_column="log2_energy",
        title="Wavelet Energy Comparison",
        xlabel="Time Scale j",
        ylabel="log2(Energy(j))",
        save_path_base=filename,
    )
