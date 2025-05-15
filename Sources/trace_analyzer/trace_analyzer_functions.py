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
def plot_pktsize_pdf_cdf_violinbox(
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

    inter_arrival_files = data_files.list_names(ADNF.INTERARRIVAL, "csv")
    for file in inter_arrival_files:
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
    stats_records = []

    if plot_type in (
        "violin-interarrival",
        "violin-pkt",
        "box-interarrival",
        "box-pkt",
    ):
        data_all = []
        labels = []

        is_violin = "violin" in plot_type
        is_packet = "pkt" in plot_type

        for target, df in df_map.items():
            df = df[df["time"] <= min_time_max]

            if is_packet:
                series = df["pkt_size"]
                title = f"{'Violin' if is_violin else 'Box'} Plot of Packet Sizes"
                xlabel = "Target"
                ylabel = "Packet Size (bytes)"
            else:
                series = df["inter_arrival"]
                title = (
                    f"{'Violin' if is_violin else 'Box'} Plot of Inter-Arrival Times"
                )
                xlabel = "Target"
                ylabel = "Inter-Arrival Time (s)"

            data_all.extend(series)
            labels.extend([target] * len(series))

            # Save mean and std for this target
            stats_records.append(
                {"target": target, "mean": series.mean(), "std": series.std()}
            )

        df_plot = pd.DataFrame({"value": data_all, "target": labels})
        if is_violin:
            sns.violinplot(x="target", y="value", data=df_plot, inner="box", cut=0)
        else:
            sns.boxplot(x="target", y="value", data=df_plot)

        plt.yscale("log")
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        # Annotate mean ± std above each plot
        for i, target in enumerate(compared_elements):
            s = df_plot[df_plot["target"] == target]["value"]
            mean_val = s.mean()
            std_val = s.std()
            plt.text(
                i,
                s.max() * 1.05,
                f"μ={mean_val:.2e}\nσ={std_val:.2e}",
                ha="center",
                va="bottom",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=1),
            )
    else:
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
                data = df["inter_arrival"].values
                data = data[
                    data > 0
                ]  # Remove zeros (log-scale issue and undefined KDE)

                # Apply KDE for smooth PDF
                kde = gaussian_kde(data)
                x_range = np.linspace(data.min(), data.max(), 1000)
                y_vals = kde(x_range)

                plt.plot(
                    x_range,
                    y_vals,
                    label=target,
                    color=colors(i),
                    linewidth=2,
                )
                plt.xscale("log")
                plt.xlabel("Inter-Arrival Time (s)")
                plt.ylabel("Density")
                plt.title("PDF of Inter-Arrival Times")

            elif plot_type == "log-pdf":
                data = df["inter_arrival"].values
                data = data[data > 0]  # drop zeros

                log_data = np.log(data)  # natural‑log is fine; base doesn't matter
                kde_log = gaussian_kde(log_data)

                log_x = np.linspace(log_data.min(), log_data.max(), 1000)
                x = np.exp(log_x)  # revert to linear space
                y = kde_log(log_x) / x  # apply Jacobian  f_log / x  →  f_t

                plt.plot(
                    x,
                    y,
                    label=target,
                    color=colors(i),
                    linewidth=2,
                )
                plt.xscale("log")
                plt.xlabel("Inter‑Arrival Time (s)")
                plt.ylabel("Density")
                plt.title("PDF of Inter‑Arrival Times (log‑domain normalised)")

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
                plt.xscale("log")
                plt.xlabel("Inter-Arrival Time (s)")
                plt.ylabel("CDF")
                plt.title("CDF of Inter-Arrival Times")

            else:
                raise ValueError(f"Unknown plot_type: {plot_type}")

    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Save plot
    file_name = pnf.mknameext(plot_type, compared_elements, "png")
    print(f"Saving plot to: {file_name}")
    plt.savefig(file_name)
    plt.close()

    # Save stats to CSV
    if stats_records:
        csv_name = pnf.mknameext(plot_type, compared_elements, "csv")
        pd.DataFrame(stats_records).to_csv(csv_name, index=False)
        print(f"Saved statistics to: {csv_name}")


def plot_bw_pps_fps(
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


def _plot_burst_analysis(
    experiment_xml_file,
    experiment_name,
    target_list=[],
    inter_arrival_threshold=0.01,  # 10ms default threshold
):
    def plot_this(target, target_list):
        return not target_list or target in target_list

    # Load experiment configuration
    c = _load_experiment_config(experiment_xml_file, experiment_name)
    data_files = ADNF(c.out_dir, c.name)
    pnf = PNF(c.out_dir, experiment_name)

    # Initialize variables
    min_time_max = None
    df_map = {}  # target -> df
    compared_elements = []

    # Load inter-arrival data
    inter_arrival_files = data_files.list_names(ADNF.INTERARRIVAL, "csv")
    for file in inter_arrival_files:
        target = ADNF.parse(file, "test_target")
        if plot_this(target, target_list):
            df = pd.read_csv(file)
            df_map[target] = df
            compared_elements.append(target)
            max_time = df["time"].max()
            if min_time_max is None or max_time < min_time_max:
                min_time_max = max_time

    print(f"Truncating all dataframes to max time: {min_time_max:.2f}s")

    # Initialize structures to hold burst metrics
    burst_stats = []
    colors = cm.get_cmap("tab10")

    burst_sizes_ax = plt.figure(figsize=(8, 6)).add_subplot(111)
    burst_durations_ax = plt.figure(figsize=(8, 6)).add_subplot(111)
    inter_burst_ax = plt.figure(figsize=(8, 6)).add_subplot(111)

    for i, (target, df) in enumerate(df_map.items()):
        df = df[df["time"] <= min_time_max]
        inter_arrivals = df["inter_arrival"].values

        # Detect bursts
        bursts = []
        current_burst = [df.iloc[0]]
        for j in range(1, len(df)):
            if inter_arrivals[j] < inter_arrival_threshold:
                current_burst.append(df.iloc[j])
            else:
                bursts.append(pd.DataFrame(current_burst))
                current_burst = [df.iloc[j]]
        if current_burst:
            bursts.append(pd.DataFrame(current_burst))

        # Compute burst metrics
        burst_sizes = sanitize([len(burst) for burst in bursts])
        burst_durations = sanitize(
            [burst["time"].iloc[-1] - burst["time"].iloc[0] for burst in bursts]
        )
        inter_burst_intervals = sanitize(
            [
                bursts[k]["time"].iloc[0] - bursts[k - 1]["time"].iloc[-1]
                for k in range(1, len(bursts))
            ]
        )
        burst_sizes = [v for v in burst_sizes if v > 0 and np.isfinite(v)]
        burst_durations = [v for v in burst_durations if v > 0 and np.isfinite(v)]
        inter_burst_intervals = [
            v for v in inter_burst_intervals if v > 0 and np.isfinite(v)
        ]

        if not burst_sizes or not burst_durations or not inter_burst_intervals:
            print(f"[WARN] No valid burst data for target: {target}. Skipping.")
            continue

        # Store statistics
        burst_stats.append(
            {
                "target": target,
                "mean_size": np.mean(burst_sizes),
                "std_size": np.std(burst_sizes),
                "mean_duration": np.mean(burst_durations),
                "std_duration": np.std(burst_durations),
                "mean_interval": np.mean(inter_burst_intervals),
                "std_interval": np.std(inter_burst_intervals),
            }
        )

        # Plot burst sizes
        sns.violinplot(y=burst_sizes, ax=burst_sizes_ax, color=colors(i), label=target)

        # Plot burst durations
        sns.violinplot(
            y=burst_durations, ax=burst_durations_ax, color=colors(i), label=target
        )

        # Plot inter-burst intervals
        sns.histplot(
            inter_burst_intervals,
            bins=50,
            ax=inter_burst_ax,
            color=colors(i),
            label=target,
            log_scale=(False, True),
        )

    # Finalize and save burst sizes plot
    burst_sizes_ax.set_yscale("log")
    burst_sizes_ax.set_title("Burst Sizes")
    burst_sizes_ax.set_ylabel("Number of Packets")
    burst_sizes_ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    burst_sizes_ax.legend()
    plt.figure(burst_sizes_ax.figure.number)
    burst_sizes_file = pnf.mknameext("burst_sizes", compared_elements, "png")
    print(f"Saving burst sizes plot to: {burst_sizes_file}")
    plt.tight_layout()
    plt.savefig(burst_sizes_file)
    plt.close()

    # Finalize and save burst durations plot
    burst_durations_ax.set_yscale("log")
    burst_durations_ax.set_title("Burst Durations")
    burst_durations_ax.set_ylabel("Duration (s)")
    burst_durations_ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    burst_durations_ax.legend()
    plt.figure(burst_durations_ax.figure.number)
    burst_durations_file = pnf.mknameext("burst_durations", compared_elements, "png")
    print(f"Saving burst durations plot to: {burst_durations_file}")
    plt.tight_layout()
    plt.savefig(burst_durations_file)
    plt.close()

    # Finalize and save inter-burst intervals plot
    inter_burst_ax.set_title("Inter-Burst Intervals")
    inter_burst_ax.set_xlabel("Interval (s)")
    inter_burst_ax.set_ylabel("Frequency")
    inter_burst_ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    inter_burst_ax.legend()
    plt.figure(inter_burst_ax.figure.number)
    inter_burst_file = pnf.mknameext("inter_burst_intervals", compared_elements, "png")
    print(f"Saving inter-burst intervals plot to: {inter_burst_file}")
    plt.tight_layout()
    plt.savefig(inter_burst_file)
    plt.close()

    """
    # Setup plot
    fig, axes = plt.subplots(3, 1, figsize=(10, 18))
    colors = cm.get_cmap("tab10")

    for i, (target, df) in enumerate(df_map.items()):
        df = df[df["time"] <= min_time_max]
        inter_arrivals = df["inter_arrival"].values

        # Detect bursts
        bursts = []
        current_burst = [df.iloc[0]]
        for j in range(1, len(df)):
            if inter_arrivals[j] < inter_arrival_threshold:
                current_burst.append(df.iloc[j])
            else:
                bursts.append(pd.DataFrame(current_burst))
                current_burst = [df.iloc[j]]
        if current_burst:
            bursts.append(pd.DataFrame(current_burst))

        # Compute burst metrics
        burst_sizes = sanitize([len(burst) for burst in bursts])
        burst_durations = sanitize(
            [burst["time"].iloc[-1] - burst["time"].iloc[0] for burst in bursts]
        )
        inter_burst_intervals = sanitize(
            [
                bursts[k]["time"].iloc[0] - bursts[k - 1]["time"].iloc[-1]
                for k in range(1, len(bursts))
            ]
        )
        burst_sizes = [v for v in burst_sizes if v > 0]
        burst_durations = [v for v in burst_durations if v > 0]
        inter_burst_intervals = [v for v in inter_burst_intervals if v > 0]

        if not burst_sizes or not burst_durations or not inter_burst_intervals:
            print(f"[WARN] No valid burst data for target: {target}. Skipping.")
            continue

        # Store statistics
        burst_stats.append(
            {
                "target": target,
                "mean_size": np.mean(burst_sizes),
                "std_size": np.std(burst_sizes),
                "mean_duration": np.mean(burst_durations),
                "std_duration": np.std(burst_durations),
                "mean_interval": np.mean(inter_burst_intervals),
                "std_interval": np.std(inter_burst_intervals),
            }
        )

        # Plot burst sizes
        sns.violinplot(y=burst_sizes, ax=axes[0], color=colors(i), label=target)
        axes[0].set_yscale("log")
        axes[0].set_title("Burst Sizes")
        axes[0].set_ylabel("Number of Packets")

        # Plot burst durations
        sns.violinplot(y=burst_durations, ax=axes[1], color=colors(i), label=target)
        axes[1].set_yscale("log")
        axes[1].set_title("Burst Durations")
        axes[1].set_ylabel("Duration (s)")

        # Plot inter-burst intervals
        sns.histplot(
            inter_burst_intervals,
            bins=50,
            ax=axes[2],
            color=colors(i),
            label=target,
            log_scale=(False, True),
        )
        axes[2].set_title("Inter-Burst Intervals")
        axes[2].set_xlabel("Interval (s)")
        axes[2].set_ylabel("Frequency")

    # Finalize plots
    for ax in axes:
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.legend()
    try:
        plt.tight_layout()
    except OverflowError as e:
        print(f"[ERROR] tight_layout() failed: {e}")

    # Save plot
    plot_file_name = pnf.mknameext("burst_analysis", compared_elements, "png")
    print(f"Saving plot to: {plot_file_name}")
    plt.savefig(plot_file_name)
    plt.close()

    # Save statistics
    stats_df = pd.DataFrame(burst_stats)
    csv_file_name = pnf.mknameext("burst_analysis", compared_elements, "csv")
    print(f"Saving statistics to: {csv_file_name}")
    stats_df.to_csv(csv_file_name, index=False)
    """


def sanitize(data):
    return [x for x in data if not (math.isinf(x) or math.isnan(x))]


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
