import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pywt
import scipy
from scipy.stats import linregress
from sqlalchemy import TEXT, Column, ForeignKey, Integer, create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from commons.connectors.alchemy_connector import AlchemyConnector
from commons.models.packet import Packet


def calc_bw_pps_fps_as_df(
    connector: AlchemyConnector, flowID: int = 0, time_granularity: float = 0.1
) -> pd.DataFrame:
    """
    Calculates the bandwidth for a given flow (or all flows) over time.

    Args:
        connector: An instantiated AlchemyConnector to the database.
        flowID: The ID of the flow to analyze. If <= 0, analyzes all flows together.
        time_granularity: The time interval (in seconds) for calculating bandwidth.

    Returns:
        A pandas DataFrame with columns:
        - point_count: sequence number of the time point,
        - time: time point in seconds,
        - bandwidth: bandwidth at the time point,
        - bandwidth_average: average bandwidth over the entire period,
        - bandwidth_variance: variance of the bandwidth over the entire period,
        - npackets: number of packets at the time point,
        - npackets_average: average number of packets over the entire period,
        - npackets_variance: variance of the number of packets over the entire period,
        - nflows: number of flows at the time point,
        - nflows_average: average number of flows over the entire period,
        - nflows_variance: variance of the number of flows over the entire period.
    """
    if time_granularity <= 0:
        raise ValueError("Time granularity must be greater than 0")

    with connector.session() as session:
        if flowID > 0:
            packets = (
                session.query(Packet)
                .filter(Packet.flowID == flowID)
                .order_by(Packet.tsSec, Packet.tsUsec)
                .all()
            )
            flows_in_period = 1
        else:
            packets = session.query(Packet).order_by(Packet.tsSec, Packet.tsUsec).all()
            flows_in_period = session.query(Packet.flowID).distinct().count()

        if not packets:
            return pd.DataFrame(
                {
                    "point_count": [],
                    "time": [],
                    "bandwidth": [],
                    "bandwidth_average": [],
                    "bandwidth_variance": [],
                    "npackets": [],
                    "npackets_average": [],
                    "npackets_variance": [],
                    "nflows": [],
                    "nflows_average": [],
                    "nflows_variance": [],
                }
            )

        timestamps = [p.timestamp_seconds for p in packets]
        packet_sizes = [p.pktSize for p in packets]
        flow_ids = [p.flowID for p in packets]

        max_time = max(timestamps)
        time_points = np.arange(0, max_time + time_granularity, time_granularity)
        num_time_points = len(time_points) - 1

        # Compute nflows per interval
        if flows_in_period > 1:
            interval_flows = [
                {
                    flow_id
                    for ts, flow_id in zip(timestamps, flow_ids)
                    if start <= ts < end
                }
                for start, end in zip(time_points[:-1], time_points[1:])
            ]
            nflows_per_interval = [len(fset) for fset in interval_flows]
        else:
            nflows_per_interval = [1] * num_time_points

        bandwidth_data = []
        packet_counts = []

        for i in range(num_time_points):
            start_time = time_points[i]
            end_time = time_points[i + 1]
            interval_packets = [
                size
                for ts, size in zip(timestamps, packet_sizes)
                if start_time <= ts < end_time
            ]
            interval_bandwidth = sum(interval_packets) * 8 / time_granularity
            bandwidth_data.append(interval_bandwidth)
            packet_counts.append(len(interval_packets))
        # bw
        avg_bandwidth = np.mean(bandwidth_data)
        bw_variance = np.var(bandwidth_data) if num_time_points > 1 else 0
        # pps
        avg_packet_count = np.mean(packet_counts)
        packet_count_variance = np.var(packet_counts) if num_time_points > 1 else 0
        # time
        midpoint_times = time_points[:-1] + time_granularity / 2
        # fps
        avg_nflows = np.mean(nflows_per_interval)
        flow_count_variance = np.var(nflows_per_interval) if num_time_points > 1 else 0

        df = pd.DataFrame(
            {
                "point_count": range(1, num_time_points + 1),
                "time": midpoint_times,
                "bandwidth": bandwidth_data,
                "bandwidth_average": [avg_bandwidth] * num_time_points,
                "bandwidth_variance": [bw_variance] * num_time_points,
                "npackets": packet_counts,
                "npackets_average": [avg_packet_count] * num_time_points,
                "npackets_variance": [packet_count_variance] * num_time_points,
                "nflows": nflows_per_interval,
                "nflows_average": [avg_nflows] * num_time_points,
                "nflows_variance": [flow_count_variance] * num_time_points,
            }
        )

        return df


def get_packet_arrival_df(connector: AlchemyConnector, flowID: int = 0) -> pd.DataFrame:
    """
    Creates a DataFrame with per-packet arrival information.

    Columns:
        - timestamp: Packet arrival time in seconds.
        - inter_arrival: Time difference between this packet and the previous one.
        - pkt_size: Size of the packet in bytes.
        - ttl: Time to Live field from the packet.

    Args:
        connector (AlchemyConnector): Active database connector.
        flowID (int): If > 0, filters packets by flow ID; otherwise includes all flows.

    Returns:
        pd.DataFrame: DataFrame with timestamp, inter-arrival time, packet size, and TTL.
    """
    with connector.session() as session:
        query = session.query(Packet).order_by(Packet.tsSec, Packet.tsUsec)
        if flowID > 0:
            packets = query.filter(Packet.flowID == flowID).all()
        else:
            packets = query.all()

        if not packets:
            return pd.DataFrame(
                columns=["timestamp", "inter_arrival", "pkt_size", "ttl"]
            )

        timestamps = [p.timestamp_seconds for p in packets]
        pkt_sizes = [p.pktSize for p in packets]
        ttls = [p.timeToLive for p in packets]

        # Calculate inter-arrival times (first is 0)
        inter_arrivals = [0] + [
            t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])
        ]

        df = pd.DataFrame(
            {
                "time": timestamps,
                "inter_arrival": inter_arrivals,
                "pkt_size": pkt_sizes,
                "ttl": ttls,
            }
        )

        return df


def calc_burst_metrics(ac: AlchemyConnector, inter_arrival_threshold=0.01):
    """
    Analyze bursts for a given target and DB connector.

    - Burst: sequence of packets where inter-arrival < threshold.
    """

    print(f"[burst] Analyzing bursts")

    df = get_packet_arrival_df(ac)  # Assumes df has 'time' column
    df = df.sort_values("time").reset_index(drop=True)

    if df.empty or len(df) < 2:
        print(f"[WARN] Not enough packets for burst analysis")
        return

    # Calculate inter-arrival times
    df["inter_arrival"] = df["time"].diff().fillna(0)

    # Detect bursts
    bursts = []
    current_burst = [df.iloc[0]]
    for i in range(1, len(df)):
        if df["inter_arrival"].iloc[i] < inter_arrival_threshold:
            current_burst.append(df.iloc[i])
        else:
            bursts.append(pd.DataFrame(current_burst))
            current_burst = [df.iloc[i]]
    if current_burst:
        bursts.append(pd.DataFrame(current_burst))

    # Compute metrics
    burst_sizes = [len(burst) for burst in bursts]
    burst_durations = [
        burst["time"].iloc[-1] - burst["time"].iloc[0] for burst in bursts
    ]
    inter_burst_intervals = [
        bursts[i]["time"].iloc[0] - bursts[i - 1]["time"].iloc[-1]
        for i in range(1, len(bursts))
    ]

    # Filter valid values
    burst_sizes = [x for x in burst_sizes if x > 0 and np.isfinite(x)]
    burst_durations = [x for x in burst_durations if x > 0 and np.isfinite(x)]
    inter_burst_intervals = [
        x for x in inter_burst_intervals if x > 0 and np.isfinite(x)
    ]

    return burst_sizes, burst_durations, inter_burst_intervals


def calc_wavelet_as_df(
    ac: AlchemyConnector,
    flowID: int = 0,
    wavelet: str = "db4",
    level: int = 5,
    bin_width: float = 0.01,  # bin width in seconds
    agg: str = "count",  # or 'sum' for bandwidth
) -> pd.DataFrame:
    """
    Perform WMEA using timestamp binning from SnifyLite DB.

    Args:
        ac (AlchemyConnector): Active database connector.
        flowID (int): Specific flow to analyze. Default is 0 (all).
        wavelet (str): Wavelet type.
        level (int): Decomposition level.
        bin_width (float): Width of time bins in seconds.
        agg (str): Aggregation: 'count' for packet rate, 'sum' for bandwidth.

    Returns:
        pd.DataFrame: DataFrame with scale, log2_energy, and target.
    """

    # --- 1. Load packet data ---
    df = get_packet_arrival_df(ac, flowID=flowID)

    if df.empty:
        print(f"No packets found for flowID={flowID}.")
        return pd.DataFrame(columns=["scale", "log2_energy", "target"])

    # --- 2. Bin timestamps into fixed intervals ---
    time_start = df["time"].min()
    time_end = df["time"].max()

    bins = np.arange(time_start, time_end + bin_width, bin_width)
    df["time_bin"] = pd.cut(df["time"], bins=bins, labels=False)

    if agg == "count":
        signal = df.groupby("time_bin").size().values  # Packet counts per bin
    elif agg == "sum":
        signal = df.groupby("time_bin")["pkt_size"].sum().fillna(0).values  # Bandwidth
    else:
        raise ValueError("agg must be 'count' or 'sum'")

    # --- 3. Ensure enough samples for wavelet decomposition ---
    signal = signal[np.isfinite(signal)]

    if len(signal) < 2**level:
        print(
            f"Not enough data points ({len(signal)}) for level {level} decomposition."
        )
        return pd.DataFrame(columns=["scale", "log2_energy", "target"])

    # --- 4. Wavelet decomposition ---
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    energies = np.array([np.sum(np.square(c)) for c in coeffs])

    # --- 5. Build DataFrame ---
    scales = np.arange(len(energies))
    log2_energies = np.log2(energies + 1e-10)  # Avoid log(0)

    result_df = pd.DataFrame(
        {"scale": scales, "log2_energy": log2_energies, "energy_abs": energies}
    )

    return result_df


def self_similarity_rs_cloudy(
    ac=None, flowID: int = 0, aggregation_levels: list[int] = [1, 5, 10, 50, 100, 500]
):
    def _rs_analysis_on_series_cloudy(series, block_sizes):
        log_ns, log_rss = [], []

        for n in block_sizes:
            if n >= len(series):
                continue

            step = max(1, n // 4)
            rs_values = []

            for start in range(0, len(series) - n + 1, step):
                block = series[start : start + n]
                mean = np.mean(block)
                dev = block - mean
                cum_dev = np.cumsum(dev)
                R = np.max(cum_dev) - np.min(cum_dev)
                S = np.std(block, ddof=1)
                if S != 0:
                    rs = R / S
                    log_ns.append(np.log2(n))
                    log_rss.append(np.log2(rs))

        rs_df = pd.DataFrame({"log_n": log_ns, "log_rs": log_rss})

        if not rs_df.empty:
            slope, _, _, _, _ = linregress(rs_df["log_n"], rs_df["log_rs"])
        else:
            slope = np.nan

        return rs_df, slope

    if ac is None:
        df = _generate_synthetic_interarrival_df()
    else:
        df = get_packet_arrival_df(ac, flowID=flowID)

    bin_width = 0.01
    time_start = df["timestamp"].min()
    time_end = df["timestamp"].max()
    bins = np.arange(time_start, time_end + bin_width, bin_width)
    df["time_bin"] = pd.cut(df["timestamp"], bins=bins, labels=False)
    bytes_per_bin = df.groupby("time_bin")["pkt_size"].sum().fillna(0).values

    # --- Cloudy R/S Plot (Figure 2a style) ---
    rs_df, _ = _rs_analysis_on_series_cloudy(
        bytes_per_bin, block_sizes=[2, 4, 8, 16, 32, 64, 128]
    )
    x = rs_df["log_n"]
    rs_df["slope_1_line"] = x * 1.0
    rs_df["slope_half_line"] = x * 0.5

    # --- Hurst vs Aggregation Level (Figure 2d style) ---
    hurst_vs_m = []
    rs_agr = []
    for m in aggregation_levels:
        n = len(bytes_per_bin) // m
        truncated = bytes_per_bin[: n * m]
        agg_series = truncated.reshape((n, m)).mean(axis=1)
        rs, hurst = _rs_analysis_on_series_cloudy(
            agg_series, block_sizes=[2, 4, 8, 16, 32]
        )
        hurst_vs_m.append((m, hurst))
        rs_agr.append({"m": m, "rs": rs})

    hurst_df = pd.DataFrame(hurst_vs_m, columns=["aggregation_level", "hurst_rs"])
    return hurst_df, rs_df, rs_agr


#############################################


def _generate_synthetic_interarrival_df(n_packets=10000, heavy_tail=True, seed=42):
    """
    Generate synthetic packet inter-arrival DataFrame.

    Parameters:
        n_packets (int): Number of packets.
        heavy_tail (bool): Whether to use heavy-tailed distribution.
        seed (int): Random seed for reproducibility.

    Returns:
        pd.DataFrame: With columns 'time', 'inter_arrival', 'pkt_size', 'ttl'
    """
    rng = np.random.default_rng(seed)
    if heavy_tail:
        inter_arrivals = rng.pareto(a=2.5, size=n_packets) * 0.01
    else:
        inter_arrivals = rng.exponential(scale=0.01, size=n_packets)

    timestamps = np.cumsum(inter_arrivals)
    pkt_sizes = rng.integers(low=60, high=1514, size=n_packets)

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "inter_arrival": inter_arrivals,
            "pkt_size": pkt_sizes,
            "ttl": 64,
        }
    )

    return df


def test_calc_self_similarity_stats_as_df():
    hurst_df, rs_df, rs_agr = self_similarity_rs_cloudy(ac=None)

    # --- Plot 1: Cloudy R/S ---
    plt.figure(figsize=(10, 6))
    plt.scatter(
        rs_df["log_n"], rs_df["log_rs"], alpha=0.4, s=15, label="R/S values", marker="+"
    )
    plt.plot(
        rs_df["log_n"],
        rs_df["slope_1_line"],
        linestyle="--",
        color="gray",
        label="slope = 1.0",
    )
    plt.plot(
        rs_df["log_n"],
        rs_df["slope_half_line"],
        linestyle="--",
        color="black",
        label="slope = 0.5",
    )
    plt.title("R/S Analysis with Multiple Windows (Cloudy Plot)")
    plt.xlabel("log(Block Size)")
    plt.ylabel("log(R/S)")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("rs_cloudy_plot.png")

    # --- Plot 2: Hurst vs Aggregation Level ---
    plt.figure(figsize=(8, 5))
    plt.plot(
        hurst_df["aggregation_level"], hurst_df["hurst_rs"], marker="o", linestyle="-"
    )
    plt.axhline(y=0.5, color="gray", linestyle="--", label="H = 0.5 (no correlation)")
    plt.axhline(y=1.0, color="black", linestyle="--", label="H = 1.0 (strong LRD)")
    plt.xscale("log")
    plt.xlabel("Aggregation Level (m)")
    plt.ylabel("Estimated Hurst Exponent")
    plt.title("Hurst vs Aggregation Level")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("hurst_vs_aggregation.png")


def plot_cloudy_rs_with_matplotlib(rs_agr, filename="rs_pox_cloud_matplotlib.png"):
    """
    Plots R/S values at each block size n (log-log) using matplotlib, like Figure 2(a) in the paper.
    No box plots — just clouds of individual dots.
    """
    plt.figure(figsize=(10, 6))

    for entry in rs_agr:
        m = entry["m"]
        rs_df = entry["rs"]
        x = rs_df["log_n"]
        y = rs_df["log_rs"]
        plt.scatter(x, y, marker="+", label=f"m={m}", alpha=0.6)

    # Add slope reference lines using one x vector
    if rs_agr:
        xref = rs_agr[0]["rs"]["log_n"]
        plt.plot(xref, xref * 1.0, "--", color="gray", label="slope=1.0")
        plt.plot(xref, xref * 0.5, "--", color="black", label="slope=0.5")

    plt.title("R/S Pox Plot (Matplotlib — Figure 2a Style)")
    plt.xlabel("log(Block Size)")
    plt.ylabel("log(R/S)")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def test_calc_self_similarity_stats_as_df_2():
    hurst_df, rs_df, rs_agr = self_similarity_rs_cloudy(ac=None)

    # This will look much closer to Figure 2(a)
    plot_cloudy_rs_with_matplotlib(rs_agr)

    # Hurst vs Aggregation
    plt.figure(figsize=(8, 5))
    plt.plot(hurst_df["aggregation_level"], hurst_df["hurst_rs"], marker="o")
    plt.axhline(0.5, color="gray", linestyle="--", label="H = 0.5")
    plt.axhline(1.0, color="black", linestyle="--", label="H = 1.0")
    plt.xscale("log")
    plt.xlabel("Aggregation Level (m)")
    plt.ylabel("Estimated Hurst")
    plt.title("Hurst vs Aggregation Level")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("hurst_vs_m_matplotlib.png")
    plt.close()


if __name__ == "__main__":
    # calc_self_similarity_stats_as_df(None)
    # test_calc_self_similarity_stats_as_df()
    test_calc_self_similarity_stats_as_df()
# test_calc_self_similarity_stats_as_df_2()
