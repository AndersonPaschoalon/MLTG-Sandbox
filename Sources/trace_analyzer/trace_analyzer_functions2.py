import argparse
import math
import os
import sys

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import gaussian_kde

import commons.pylang.pylang as pl
import trace_analyzer.analyzer.bandwidth as bandwidth
import trace_analyzer.plots.plots as plots
from commons.config.experiment_config import ExperimentConfig
from commons.connectors.alchemy_connector import AlchemyConnector
from commons.enviroment.env import Env
from commons.enviroment.memory_store import MemoryStore
from commons.naming.analysis_data_name_formatter import (
    AnalysisDataNameFormatter as ADNF,
)
from commons.naming.plot_name_formatter import PlotNameFormatter as PNF
from commons.naming.raw_data_name_formatter import RawDataNameFormatter as RDNF
from trace_analyzer.loader.sniffer_wrapper import SnifferWrapper

env_file = ".trace_analyzer_env.json"
env = Env()
mem = MemoryStore()
CMD_RM_ENV = "--rm-env"
CMD_MAKE_ENV = "--mk-env"
CMD_ANALYZE = "--analyze"
CMD_LIST_TR = "--list-traces"


###############################################################################
# Enviroment utilities
###############################################################################


def create_env(ex_xml, ex_name):
    print(f"Importing experiment from: {ex_xml} with name: {ex_name}")
    if os.path.exists(env_file):
        print(
            f"Enviroment for {ex_xml} alread created. Use {CMD_RM_ENV} to remove enviroment."
        )
        return
    config = ExperimentConfig.get_by_name(ex_xml, ex_name)
    env.ex_xml = ex_xml
    env.ex_name = ex_name
    env.ex_loaded = False
    env.ex_analyzed = False
    env.save(env_file)


def rm_env():
    if os.path.exists(env_file):
        print(f"rm {env_file}")
        os.remove(env_file)
        return
    print(f"Enviroment file {env_file} not found.")


def load_env():
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"No experiment was loaded yet.")
    env.load(env_file)
    ex_xml = env.ex_xml
    ex_name = env.ex_name
    print(f"Importing experiment from: {ex_xml} with name: {ex_name}")
    if not os.path.exists(ex_xml):
        raise FileNotFoundError(f"{ex_xml}")
    config = ExperimentConfig.get_by_name(ex_xml, ex_name)
    list_configs = ExperimentConfig.load(env.ex_xml)

    # Register basic objects
    mem.list_configs = list_configs
    mem.c = config
    mem.rpcap = RDNF(config.out_dir, config.name, "pcap")
    mem.rcsv = RDNF(config.out_dir, config.name, "pcap")
    mem.anf = ADNF(config.out_dir, config.name)
    mem.pnf = PNF(config.out_dir, ex_name)
    mem.ex_name = config.name
    mem.ex_dir = config.experiment_dir()
    mem.sniffer = SnifferWrapper(config.experiment_dir(), config.name)
    mem.ground_truth = config.pcap
    mem.client_pcaps = mem.rpcap.list_names("capture", "pcap", "client")
    mem.server_pcaps = mem.rpcap.list_names("capture", "pcap", "server")

    # Register after --mk-env objects
    if env.ex_loaded:
        ltraces = mem.sniffer.list_loaded_traces()
        traces_target = []
        for trace in ltraces:
            target = mem.rpcap.parse(trace, RDNF.TEST_TARGET)
            tt = (trace, target)
            traces_target.append(tt)
        mem.traces_terget = traces_target

    # Register after --analyze objects
    if env.ex_analyzed:
        # bw data files
        bwdata_target = []
        bwdata_files = mem.anf.list_names(ADNF.BW_PPS_FPS, "csv")
        for file in bwdata_files:
            target = mem.anf.parse(file, "test_target")
            bt = (file, target)
            bwdata_target.append(bt)
        mem.bwdata_target = bwdata_target
        # interarrival data files
        interdata_target = []
        interdata_files = mem.anf.list_names(ADNF.INTERARRIVAL, "csv")
        for file in interdata_files:
            target = mem.anf.parse(file, "test_target")
            bt = (file, target)
            interdata_target.append(bt)
        mem.interdata_target = interdata_target
    print("load_env done")


###############################################################################
# Analysis calls
###############################################################################


def list_experiments():
    """
    Lists all traces loaded into the sniffer database for each experiment defined in the XML file.

    This function:
    1. Loads all experiment configurations from the given XML file (supports multiple experiments).
    2. For each experiment, checks if its sniffer database has been initialized.
    3. If initialized, lists all traces that were previously loaded into the sniffer database.
    4. Prints a summary of all loaded traces.

    """
    load_env()
    lout = []
    c: ExperimentConfig
    for c in mem.list_configs:
        if not os.path.exists(c.experiment_db_dir()):
            print(f"Experiment {c.experiment_dir()} wasn't loaded yet.")
            continue
        sniffer = SnifferWrapper(c.experiment_dir(), c.name)
        l = sniffer.list_loaded_traces()
        lout.append(l)
    print("Loaded experiments.traces are:")
    for l in lout:
        for i in l:
            print(f"-\t{i}")


def load_experiment():
    """
    Load packet capture data into the experiment sniffer database.

    Step-by-step:
    1. Load the environment configuration with `load_env()`.
    2. Abort if the experiment has already been loaded (based on `env.ex_loaded`).
    3. Call `mem.sniffer.exec()` on the ground-truth pcap.
    4. Iterate over client pcaps and parse them into the sniffer database.
    5. On error, delete the environment and raise the exception.
    6. Mark the experiment as loaded and save to disk.

    Returns:
        bool: True if load was performed; False if it was already loaded.
    """
    load_env()
    if env.ex_loaded:
        print(
            f"Experiment {env.ex_name} already loaded. If you want to reload it use {CMD_RM_ENV} before."
        )
        return False
    try:
        mem.sniffer.exec(mem.ground_truth)
        for pcap in mem.client_pcaps:
            mem.sniffer.exec(pcap)
    except Exception as ex:
        print(f"Error while trying to load experiment data: {ex}")
        rm_env()
        raise ex
    env.ex_loaded = True
    env.save(env_file)
    return True


def analyze_experiment():
    """
    Analyze parsed data and generate CSVs for plotting (bandwidth and interarrival).

    Step-by-step:
    1. Load the environment using `load_env()`.
    2. Abort if the experiment was already analyzed (`env.ex_analyzed`).
    3. For each loaded trace:
        - Open a DB connector with `mem.sniffer.flowdb_connector`.
        - Compute and export:
            a. Bandwidth / packets per second / flows per second (`bw_pps_fps`)
            b. Packet interarrival times (`interarrival`)
    4. Mark the experiment as analyzed and update the environment file.

    Notes:
    - Intermediate CSVs are stored in paths based on `ADNF`.
    - This function assumes the experiment was already loaded successfully.
    """

    def bw_pps_fps(target: str, ac: AlchemyConnector):
        df = bandwidth.calc_bw_pps_fps_as_df(ac)
        csv_file = mem.anf.mknameext(ADNF.BW_PPS_FPS, target, "csv")
        df.to_csv(csv_file, index=False)
        return csv_file

    def interarrival(target: str, ac: AlchemyConnector):
        df = bandwidth.get_packet_arrival_df(ac)
        csv_file = mem.anf.mknameext(ADNF.INTERARRIVAL, target, "csv")
        df.to_csv(csv_file, index=False)
        return csv_file

    load_env()
    if env.ex_analyzed:
        print(
            f"Experiment {env.ex_name} already analyzed. "
            f"If you want to do it again, it use {CMD_RM_ENV} to remove enviroment and {CMD_MAKE_ENV} and {CMD_ANALYZE} "
            f"to load enviroment and perform analysis. "
        )
        return False

    for trace, target in mem.traces_terget:
        print(f"Loading db connector for trace {trace}")
        ac: AlchemyConnector = mem.sniffer.flowdb_connector(trace)
        # Calculate and exporting bandwidth, packets per second and flows per second
        bw_pps_fps(target, ac)
        interarrival(target, ac)

    env.ex_analyzed = True
    env.save(env_file)


###############################################################################
# Plot utilities
###############################################################################


def run_tests():
    print("#########")
    target_list = []
    load_analysis_data(target_list=target_list)
    # plot_violin_interarrival(target_list=target_list)
    # plot_violin_pkt(target_list=target_list)
    # plot_box_interarrival(target_list=target_list)
    # plot_box_pkt(target_list=target_list)
    # plot_interarrival_pdf(target_list=target_list)
    # plot_interarrival_cdf(target_list=target_list)
    plot_interarrival_by_index(target_list=target_list)
    plot_bw_pps_fps_refactored("bandwidth", target_list=None)
    plot_bw_pps_fps_refactored("packet_per_second", target_list=None)
    plot_bw_pps_fps_refactored("flow_per_second", target_list=None)
    plot_pktsize_histogram(target_list=None)
    plot_bandwidth_cdf()
    plot_packet_load_cdf()
    plot_payload_size_cdf()


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


def _prepare_distribution_data(target_list: list[str]):
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


def load_analysis_data(target_list=[]):
    """
    Load post-analysis data from CSVs, prepare in-memory DataFrames and compute min time ranges.

    Step-by-step:
    1. Load the current experiment environment via `load_env()`.
    2. For each inter-arrival CSV file:
        - Load the DataFrame.
        - Track the max `time` for each and update the global min of all max times.
        - Store each DataFrame in a map for quick access.
    3. Repeat the same process for bandwidth/pps/fps CSVs.
    4. Register all values into the memory store (`mem`) for downstream plotting.

    Args:
        target_list (list[str], optional): Filter for which targets to load. If empty, load all.

    Stored in `mem`:
        - inter_df_map: dict of target → inter-arrival DataFrame
        - inter_min_time_max: float, shortest max time among inter-arrival DFs
        - bw_df_map: dict of target → bandwidth/pps/fps DataFrame
        - bw_min_time_max: float, shortest max time among BW DFs
    """
    load_env()
    # Load and store relevant DataFrames, and compute the shortest time range
    inter_min_time_max = None
    inter_df_map = {}  # target -> df
    compared_elements = []

    # for inter-arrival data
    for file, target in mem.interdata_target:
        if _plot_this(target, target_list):
            df = pd.read_csv(file)
            inter_df_map[target] = df
            compared_elements.append(target)
            max_time = df["time"].max()
            if inter_min_time_max is None or max_time < inter_min_time_max:
                inter_min_time_max = max_time
    mem.inter_df_map = inter_df_map
    mem.inter_min_time_max = inter_min_time_max

    # Load and store relevant DataFrames, and compute the shortest time range
    bw_min_time_max = None
    bw_df_map = {}  # target -> df
    compared_elements = []

    for file, target in mem.bwdata_target:
        if _plot_this(target, target_list):
            df = pd.read_csv(file)
            bw_df_map[target] = df
            compared_elements.append(target)
            max_time = df["time"].max()
            if bw_min_time_max is None or max_time < bw_min_time_max:
                bw_min_time_max = max_time
    mem.bw_min_time_max = bw_min_time_max
    mem.bw_df_map = bw_df_map


###############################################################################
# Plot calls
###############################################################################


def plot_violin_interarrival(target_list=None):
    """
    Plot violin distribution of inter-arrival times for each target.

    Filters data up to mem.inter_min_time_max and optionally by target_list.
    """

    filtered_df_map, compared_targets = _prepare_distribution_data(target_list)
    filename = mem.pnf.mkname("violin-interarrival", compared_targets)

    # Plot
    plots.plot_distribution_plot(
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

    Filters data up to mem.inter_min_time_max and optionally by target_list.
    """
    filtered_df_map, compared_targets = _prepare_distribution_data(target_list)
    filename = mem.pnf.mkname("violin-pkt", compared_targets)

    plots.plot_distribution_plot(
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

    Filters data up to mem.inter_min_time_max and optionally by target_list.
    """
    filtered_df_map, compared_targets = _prepare_distribution_data(target_list)
    filename = mem.pnf.mkname("box-interarrival", compared_targets)

    plots.plot_distribution_plot(
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

    Filters data up to mem.inter_min_time_max and optionally by target_list.
    """
    filtered_df_map, compared_targets = _prepare_distribution_data(target_list)
    filename = mem.pnf.mkname("box-pkt", compared_targets)

    plots.plot_distribution_plot(
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
    if target_list:
        df_map = {k: v for k, v in mem.inter_df_map.items() if k in target_list}
    else:
        df_map = mem.inter_df_map
    targets = list(df_map.keys())

    filename = mem.pnf.mkname("pdf-interarrival", targets)
    plots.plot_pdf(
        df_map=df_map,
        column="inter_arrival",
        title="PDF of Inter-Arrival Times (log-domain normalized)",
        xlabel="Inter-Arrival Time (s)",
        ylabel="Density",
        save_path_base=filename,
        target_list=target_list,
        log_x=True,
        log_y=False,
    )


def plot_interarrival_cdf(target_list=None):
    """
    Wrapper to plot the CDF of inter-arrival times using the generic plot_cdf().
    Filters targets if target_list is provided.
    """
    if target_list:
        df_map = {k: v for k, v in mem.inter_df_map.items() if k in target_list}
    else:
        df_map = mem.inter_df_map
    targets = list(df_map.keys())
    filename = mem.pnf.mkname("cdf-interarrival", targets)

    plots.plot_cdf(
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
    if target_list:
        df_map = {k: v.copy() for k, v in mem.inter_df_map.items() if k in target_list}
    else:
        df_map = {k: v.copy() for k, v in mem.inter_df_map.items()}

    # Ensure 'index' column exists
    for df in df_map.values():
        df.reset_index(drop=True, inplace=True)
        df["index"] = df.index

    targets = list(df_map.keys())
    filename = mem.pnf.mkname("interarrival_by_index", targets)

    plots.plot_line(
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
    Plot bandwidth, packets/sec or flows/sec using preloaded mem.bw_df_map and mem.bw_min_time_max.
    """
    target_list = target_list or []
    df_map = {
        k: v for k, v in mem.bw_df_map.items() if not target_list or k in target_list
    }
    compared = list(df_map.keys())
    tmax = mem.bw_min_time_max

    metric_map = {
        "bandwidth": ("bandwidth", "bandwidth_average", "Bandwidth (bps)"),
        "packet_per_second": ("npackets", "npackets_average", "Packets per Second"),
        "flow_per_second": ("nflows", "nflows_average", "Flows per Second"),
    }

    if plot_type not in metric_map:
        raise ValueError(f"Unknown plot_type '{plot_type}'")

    raw_col, avg_col, y_label = metric_map[plot_type]

    save_path = mem.pnf.mkname(plot_type, compared)

    plots.plot_timeseries(
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
    if target_list:
        df_map = {k: v for k, v in mem.inter_df_map.items() if k in target_list}
    else:
        df_map = mem.inter_df_map

    colors = cm.get_cmap("tab10")
    for i, (target, df) in enumerate(df_map.items()):
        df = df[df["time"] <= mem.bw_min_time_max]
        save_path = mem.pnf.mkname("histogram-pktsize", [target])
        color = colors(i % 10)
        plots.plot_histogram(
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
    Uses preloaded and truncated data from mem.bw_df_map and mem.bw_min_time_max.
    """
    if target_list:
        df_map = {k: v for k, v in mem.bw_df_map.items() if k in target_list}
    else:
        df_map = mem.bw_df_map

    truncated_map = {
        target: df[df["time"] <= mem.bw_min_time_max] for target, df in df_map.items()
    }

    save_path_base = mem.pnf.mkname("bandwidth_cdf", list(truncated_map.keys()))
    plots.plot_cdf(
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
    Uses preloaded and truncated interarrival data from mem.inter_df_map and mem.inter_min_time_max.
    """
    if target_list:
        df_map = {k: v for k, v in mem.inter_df_map.items() if k in target_list}
    else:
        df_map = mem.inter_df_map

    truncated_map = {
        target: df[df["time"] <= mem.inter_min_time_max]
        for target, df in df_map.items()
    }

    save_path_base = mem.pnf.mkname("payload_size_cdf", list(truncated_map.keys()))
    plots.plot_cdf(
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
    Uses preloaded and truncated data from mem.bw_df_map and mem.bw_min_time_max.
    """
    if target_list:
        df_map = {k: v for k, v in mem.bw_df_map.items() if k in target_list}
    else:
        df_map = mem.bw_df_map

    truncated_map = {
        target: df[df["time"] <= mem.bw_min_time_max] for target, df in df_map.items()
    }

    save_path_base = mem.pnf.mkname("packet_load_cdf", list(truncated_map.keys()))
    plots.plot_cdf(
        df_map=truncated_map,
        column="npackets",
        xlabel="Packets per Second",
        title="Packet Load Distribution (CDF)",
        save_path_base=save_path_base,
        log_scale=True,
    )


if __name__ == "__main__":
    # create_env("scripts/xml/sample_tests.xml", "Banana")
    # load_env()
    # print(mem)
    cmd_list_tr = False
    cmd_mk_env = False
    cmd_rm_env = False
    cmd_analyze = False
    test05 = True

    # --list-traces
    if cmd_list_tr:
        list_experiments()
    # --mk-env
    if cmd_mk_env:
        create_env("scripts/xml/sample_tests.xml", "Banana")
        load_experiment()
        list_experiments()
    # --rm-env
    if cmd_rm_env:
        rm_env()
    elif cmd_analyze:
        analyze_experiment()
    elif test05:
        run_tests()
