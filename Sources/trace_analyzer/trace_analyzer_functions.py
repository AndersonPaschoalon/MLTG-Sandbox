import argparse
import os
import sys

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import commons.pylang.pylang as pl
import trace_analyzer.analyzer.bandwidth as bandwidth
from commons.config.experiment_config import ExperimentConfig
from commons.connectors.alchemy_connector import AlchemyConnector
from commons.naming.analysis_data_name_formatter import (
    AnalysisDataNameFormatter as ADNF,
)
from commons.naming.plot_name_formatter import PlotNameFormatter as PNF
from commons.naming.raw_data_name_formatter import RawDataNameFormatter as RDNF
from trace_analyzer.loader.sniffer_wrapper import SnifferWrapper


def load_experiment(experiment_xml_file, experiment_name):
    """
    Loads experiment metadata and parses all associated pcap files into the sniffer database.

    This utility function performs the following steps:
    1. Loads experiment configuration from the specified XML file.
    2. Lists all generated `.pcap` files associated with the given experiment name.
    3. Initializes the sniffer database for the experiment.
    4. Parses and stores packet data into the database.
    5. Parses and stores packet data from all experiment runs (client captures) into the same database.

    Args:
        experiment_xml_file (str): Path to the XML file describing the experiment setup.
        experiment_name (str): Name of the experiment to load.
    """
    config = _load_experiment_config(experiment_xml_file, experiment_name)
    print("#1 Loading data from Pcaps")
    pcap_fmt = RDNF(config.out_dir, config.name, "pcap")
    # list all *.pcap and client catpures. no tool_under_test means all will be returned.
    file_list = pcap_fmt.list_names("capture", "pcap", "client")
    sniffer = SnifferWrapper(config.experiment_dir(), config.name)
    # store ground truth
    sniffer.exec(config.pcap)
    for f in file_list:
        # store each experiment run
        # if i need recover this data later, I should use SnifferWrapper.trace_entry_name()
        sniffer.exec(f)


def list_experiments(experiment_xml_file):
    """
    Lists all traces loaded into the sniffer database for each experiment defined in the XML file.

    This function:
    1. Loads all experiment configurations from the given XML file (supports multiple experiments).
    2. For each experiment, checks if its sniffer database has been initialized.
    3. If initialized, lists all traces that were previously loaded into the sniffer database.
    4. Prints a summary of all loaded traces.

    Args:
        experiment_xml_file (str): Path to the XML file containing one or more experiment configurations.

    """
    list_configs = _load_experiment_config(experiment_xml_file, "*")
    lout = []
    c: ExperimentConfig
    for c in list_configs:
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


def analyze_experiment(experiment_xml_file, experiment_name):
    """ """

    def bw_pps_fps(trace: str, ac: AlchemyConnector):
        print(f"Calculating bandwidth, pps and fps {trace}")
        df = bandwidth.calc_bw_pps_fps_as_df(ac)
        # Save the results. File name is bw_pps_fps.<tool>.csv, where tool can be
        # evaluated from the trace name using RDNF.parse()
        target = pcap.parse(trace, RDNF.TEST_TARGET)
        csv_file = fmt.mknameext(ADNF.BW_PPS_FPS, target, "csv")
        print(f"Saving results to {csv_file}")
        df.to_csv(csv_file, index=False)
        return csv_file

    def interarrival(trace: str, ac: AlchemyConnector):
        df = bandwidth.get_packet_arrival_df(ac)
        target = pcap.parse(trace, RDNF.TEST_TARGET)
        csv_file = fmt.mknameext(ADNF.INTERARRIVAL, target, "csv")
        print(f"Saving results to {csv_file}")
        df.to_csv(csv_file, index=False)
        return csv_file

    print(f"Analyzing experiment: {experiment_name} from file: {experiment_xml_file}")
    c = _load_experiment_config(experiment_xml_file, experiment_name)
    sniffer = SnifferWrapper(c.experiment_dir(), c.name)
    ltraces = sniffer.list_loaded_traces()
    fmt = ADNF(c.out_dir, c.name)
    pcap = RDNF(c.out_dir, c.name, "pcap")
    for t in ltraces:
        print(f"Loading db connector for trace {t}")
        ac: AlchemyConnector = sniffer.flowdb_connector(t)
        # Calculate and exporting bandwidth, packets per second and flows per second
        bw_pps_fps(t, ac)
        interarrival(t, ac)


# packet_size, pdf, cdf
def _plot_psh_pdf_cdf(
    experiment_xml_file, experiment_name, target_list=[], plot_type="packet_size"
):
    def plot_this(target, target_list):
        return not target_list or target in target_list

    c = _load_experiment_config(experiment_xml_file, experiment_name)
    data_files = ADNF(c.out_dir, c.name)
    pnf = PNF(c.out_dir, experiment_name)

    # Load and store relevant DataFrames, and compute the shortest time range
    min_time_max = None
    df_map = {}  # target -> df
    compared_elements = []

    for file in data_files.list_names(ADNF.INTERARRIVAL, "csv"):
        target = ADNF.parse(file, "test_target")
        if plot_this(target, target_list):
            df = pd.read_csv(file)
            df_map[target] = df
            compared_elements.append(target)
            max_time = df["time"].max()
            if min_time_max is None or max_time < min_time_max:
                min_time_max = max_time

    print(f"Truncating all dataframes to max time: {min_time_max:.2f}s")

    # Setup plot
    plt.figure(figsize=(10, 6))
    colors = cm.get_cmap("tab10")

    for i, (target, df) in enumerate(df_map.items()):
        df = df[df["time"] <= min_time_max]

        if plot_type == "packet_size":
            plt.hist(
                df["pkt_size"],
                bins=30,
                alpha=0.5,
                label=target,
                color=colors(i),
                edgecolor="black",
            )
            plt.xlabel("Packet Size (bytes)")
            plt.ylabel("Frequency")
            plt.title("Packet Size Distribution")

        elif plot_type == "pdf":
            sns.histplot(
                df["inter_arrival"],
                bins=50,
                kde=True,
                stat="density",
                label=target,
                color=colors(i),
            )
            plt.xlabel("Inter-Arrival Time (s)")
            plt.ylabel("Density")
            plt.title("PDF of Inter-Arrival Times")

        elif plot_type == "cdf":
            sorted_data = np.sort(df["inter_arrival"])
            cdf = np.arange(len(sorted_data)) / float(len(sorted_data))
            plt.plot(
                sorted_data,
                cdf,
                marker=".",
                linestyle="none",
                label=target,
                color=colors(i),
            )
            plt.xlabel("Inter-Arrival Time (s)")
            plt.ylabel("CDF")
            plt.title("CDF of Inter-Arrival Times")

        else:
            raise ValueError(f"Unknown plot_type: {plot_type}")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Save plot
    file_name = pnf.mknameext(plot_type, compared_elements, "png")
    print(f"Saving plot to: {file_name}")
    plt.savefig(file_name)
    plt.close()


def _plot_bw_pps_fps(
    experiment_xml_file, experiment_name, target_list=[], plot_type="bandwidth"
):
    def plot_this(target, target_list):
        return not target_list or target in target_list

    print(
        f"Plotting '{plot_type}' analysis for experiment: {experiment_name} from file: {experiment_xml_file}"
    )
    c = _load_experiment_config(experiment_xml_file, experiment_name)
    data_files = ADNF(c.out_dir, c.name)
    pnf = PNF(c.out_dir, experiment_name)

    # Map plot_type to correct column names
    metric_map = {
        "bandwidth": ("bandwidth", "bandwidth_average"),
        "packet_per_second": ("npackets", "npackets_average"),
        "flow_per_second": ("nflows", "nflows_average"),
    }

    if plot_type not in metric_map:
        raise ValueError(
            f"Unsupported plot_type '{plot_type}'. Choose from {list(metric_map.keys())}"
        )

    raw_col, avg_col = metric_map[plot_type]

    # Load and store relevant DataFrames, and compute the shortest time range
    min_time_max = None
    df_map = {}  # target -> df
    compared_elements = []

    for file in data_files.list_names(ADNF.BW_PPS_FPS, "csv"):
        target = ADNF.parse(file, "test_target")
        if plot_this(target, target_list):
            df = pd.read_csv(file)
            df_map[target] = df
            compared_elements.append(target)
            max_time = df["time"].max()
            if min_time_max is None or max_time < min_time_max:
                min_time_max = max_time

    print(f"Truncating all dataframes to max time: {min_time_max:.2f}s")

    # Setup plot
    plt.figure(figsize=(10, 6))
    colors = cm.get_cmap("tab10")

    for i, (target, df) in enumerate(df_map.items()):
        df_trunc = df[df["time"] <= min_time_max]
        color = colors(i % 10)
        plt.plot(
            df_trunc["time"],
            df_trunc[raw_col],
            linewidth=1,
            label=f"{target} (raw)",
            color=color,
        )
        plt.plot(
            df_trunc["time"],
            df_trunc[avg_col],
            linewidth=2.5,
            label=f"{target} (avg)",
            color=color,
        )

    # Axis labels and title
    y_labels = {
        "bandwidth": "Bandwidth (bps)",
        "packet_per_second": "Packets per Second",
        "flow_per_second": "Flows per Second",
    }

    plt.xlabel("Time (s)")
    plt.ylabel(y_labels[plot_type])
    plt.title(f"{y_labels[plot_type]} vs Time — {experiment_name}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save plot
    file_name = pnf.mknameext(plot_type, compared_elements, "png")
    print(f"Saving plot to: {file_name}")
    plt.savefig(file_name)
    plt.close()


def _load_experiment_config(experiment_xml_file, experiment_name="*"):
    print(
        f"Importing experiment from: {experiment_xml_file} with name: {experiment_name}"
    )
    if not os.path.exists(experiment_xml_file):
        raise FileNotFoundError(f"{experiment_xml_file}")
    if experiment_name == "*":
        list_configs = ExperimentConfig.load(experiment_xml_file)
        return list_configs
    else:
        config = ExperimentConfig.get_by_name(experiment_xml_file, experiment_name)
        return config
