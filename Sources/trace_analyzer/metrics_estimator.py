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


"""
def calc_self_similarity_stats_as_df(
    ac: AlchemyConnector,
    flowID: int = 0,
    agregation_levels_m=[1, 5, 10, 50, 100, 500, 1000],
    max_timestamp: float = 0,  # 0 means no limit. Owerwise, only consider packets with timestamp <= max_timestamp.
) -> pd.DataFrame:
    ""
    Calculate self-similarity statistics for multiple aggregation levels.

    Returns:
        dict[str, pd.DataFrame]:
            - 'rs': DataFrame for R/S plot (log(m), log(R/S))
            - 'var': DataFrame for Variance-Time plot (log(m), log(Var))
            - 'hurst': DataFrame summarizing Hurst exponents from each method
    ""

    # --- 1. Load packet data ---
    if ac:
        df = get_packet_arrival_df(ac, flowID=flowID)
    else:
        df = _generate_synthetic_interarrival_df(
            n_packets=10000, heavy_tail=True, seed=42
        )

    if df.empty:
        print(f"No packets found for flowID={flowID}.")
        return {
            "rs": pd.DataFrame(),
            "var": pd.DataFrame(),
            "hurst": pd.DataFrame(),
        }

    # Limit to max_timestamp if set
    if max_timestamp > 0:
        df = df[df["time"] <= max_timestamp]

    # For analysis, let's work with inter-arrival times
    signal = df["inter_arrival"].values

    # To accumulate results
    rs_data = []
    var_data = []

    # For slope estimation → Hurst
    rs_logs = []
    var_logs = []

    agg_logs = []

    for m in agregation_levels_m:
        # --- 2. Aggregate signal by level m ---
        # Using non-overlapping blocks of size m:
        # e.g., for m=10, each new value is sum of 10 inter-arrivals
        num_blocks = len(signal) // m
        if num_blocks == 0:
            print(f"Not enough data for aggregation level m={m}. Skipping.")
            continue

        agg_signal = signal[: num_blocks * m].reshape(-1, m).sum(axis=1)

        # --- 3. R/S statistic ---
        mean_agg = np.mean(agg_signal)
        Z = np.cumsum(agg_signal - mean_agg)
        R = np.max(Z) - np.min(Z)
        S = np.std(agg_signal, ddof=1)

        rs_stat = R / S if S != 0 else np.nan

        # --- 4. Variance ---
        var_stat = np.var(agg_signal)

        # --- 5. Accumulate data ---
        rs_data.append({"m": m, "rs": rs_stat})
        var_data.append({"m": m, "var": var_stat})

        # For Hurst estimation via slope: log-log points
        if rs_stat > 0 and var_stat > 0:
            rs_logs.append(np.log(rs_stat))
            var_logs.append(np.log(var_stat))
            agg_logs.append(np.log(m))

    # --- 6. Prepare DataFrames ---

    rs_df = pd.DataFrame(rs_data)
    var_df = pd.DataFrame(var_data)

    rs_df["log_m"] = np.log(rs_df["m"])
    rs_df["log_rs"] = np.log(rs_df["rs"])

    var_df["log_m"] = np.log(var_df["m"])
    var_df["log_var"] = np.log(var_df["var"])

    # --- 7. Linear regression to estimate Hurst exponents ---

    # R/S: log(R/S) = H log(m) + const → slope = H
    rs_slope, _, _, _, _ = scipy.stats.linregress(agg_logs, rs_logs)
    hurst_rs = rs_slope

    # Variance: log(Var) = (2H - 2) log(m) + const → slope = 2H - 2 → H = (slope + 2)/2
    var_slope, _, _, _, _ = scipy.stats.linregress(agg_logs, var_logs)
    hurst_var = (var_slope + 2) / 2

    # --- 8. Optionally, periodogram method ---

    # Using scipy's Welch method for spectral density estimation
    freqs, power = scipy.signal.welch(signal, scaling="density")

    periodogram_df = pd.DataFrame(
        {
            "freq": freqs,
            "power": power,
            "log_freq": np.log(freqs + 1e-8),
            "log_power": np.log(power + 1e-8),
        }
    )

    # Linear fit on low frequency region (e.g., first 10% of freqs)
    low_freq = int(0.1 * len(freqs))
    slope, _, _, _, _ = scipy.stats.linregress(
        periodogram_df["log_freq"][:low_freq], periodogram_df["log_power"][:low_freq]
    )

    # Spectral slope β → H = (1 + β) / 2
    hurst_spec = (1 + abs(slope)) / 2  # Take abs to avoid negative

    # --- 9. Summary DataFrame ---

    hurst_df = pd.DataFrame(
        {"method": ["rs", "var", "spec"], "hurst": [hurst_rs, hurst_var, hurst_spec]}
    )

    # --- 10. Return all DataFrames ---

    return {
        "rs": rs_df,
        "var": var_df,
        "periodogram": periodogram_df,
        "hurst": hurst_df,
    }
"""


def calc_self_similarity_stats_as_df(
    ac: AlchemyConnector,
    flowID: int = 0,
    agregation_levels_m=[1, 5, 10, 50, 100, 500, 1000],
    max_timestamp: float = 0,  # 0 means no limit. Owerwise, only consider packets with timestamp <= max_timestamp.
) -> pd.DataFrame:
    """
    Calculate self-similarity statistics for multiple aggregation levels.

    Returns:
        dict[str, pd.DataFrame]:
            - 'rs': DataFrame for R/S plot (log(m), log(R/S))
            - 'var': DataFrame for Variance-Time plot (log(m), log(Var))
            - 'hurst': DataFrame summarizing Hurst exponents from each method
    """

    def _calc_aggregate_series(series, m):
        n = len(series) // m
        truncated = series[: n * m]
        reshaped = truncated.reshape((n, m))
        aggregated = reshaped.mean(axis=1)  # average over each block
        return aggregated

    def _calc_aggregated_series_dict(df):
        # Limit to max_timestamp if set
        if max_timestamp > 0:
            df = df[df["time"] <= max_timestamp]

        bin_width = 0.01  # 10 milliseconds
        time_start = df["timestamp"].min()
        time_end = df["timestamp"].max()

        bins = np.arange(time_start, time_end + bin_width, bin_width)
        df["time_bin"] = pd.cut(df["timestamp"], bins=bins, labels=False)
        bytes_per_bin = df.groupby("time_bin")["pkt_size"].sum().fillna(0).values
        pkts_per_bin = df.groupby("time_bin").size().values

        aggregated_series_dict = {}

        for m in agregation_levels_m:
            agg_bytes = _calc_aggregate_series(bytes_per_bin, m)
            agg_pkts = _calc_aggregate_series(pkts_per_bin, m)
            aggregated_series_dict[m] = {"bytes": agg_bytes, "pkts": agg_pkts}

        return aggregated_series_dict

    def _calc_rs_for_series(series):
        """
        Compute the rescaled range (R/S) statistic for a series.
        """
        n = len(series)
        mean = np.mean(series)
        dev = series - mean
        cum_dev = np.cumsum(dev)
        R = np.max(cum_dev) - np.min(cum_dev)
        S = np.std(series, ddof=1)
        if S == 0:
            return np.nan
        return R / S

    def _estimate_hurst(rs_df):
        """
        Estimate Hurst exponent from R/S plot.
        """
        slope, intercept, r_value, p_value, std_err = linregress(
            rs_df["log_m"], rs_df["log_rs"]
        )
        return slope

    # --- 1. Load packet data ---
    if ac:
        df = get_packet_arrival_df(ac, flowID=flowID)
    else:
        df = _generate_synthetic_interarrival_df(
            n_packets=30000, heavy_tail=True, seed=42
        )
    if df.empty:
        print(f"No packets found for flowID={flowID}.")
        raise ValueError(
            f"No packets found for flowID={flowID}. Please check the database or use synthetic data."
        )

    aggregated_series_dict = _calc_aggregated_series_dict(df)

    rs_results = []
    var_results = []

    for m in agregation_levels_m:
        # TODO
        ...

    print("########################")
    print("########################")
    print("########################")


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
    np.random.seed(seed)

    if heavy_tail:
        # Pareto distribution for heavy-tailed inter-arrivals
        inter_arrivals = np.random.pareto(a=2.5, size=n_packets) + 0.1
    else:
        # Exponential for memoryless inter-arrivals
        inter_arrivals = np.random.exponential(scale=1.0, size=n_packets)
    inter_arrivals = inter_arrivals * 0.001

    timestamps = np.cumsum(inter_arrivals)

    pkt_sizes = np.random.randint(40, 1500, size=n_packets)  # Ethernet-like sizes
    ttls = np.random.randint(32, 128, size=n_packets)  # Some TTL range

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "inter_arrival": inter_arrivals,
            "pkt_size": pkt_sizes,
            "ttl": ttls,
        }
    )

    return df


def test_calc_self_similarity_stats_as_df():
    result = calc_self_similarity_stats_as_df(None)
    # Plot R/S
    rs_df = result["rs"]
    plt.figure(figsize=(8, 4))
    plt.plot(rs_df["log_m"], rs_df["log_rs"], "o-", label="R/S")
    plt.xlabel("log(m)")
    plt.ylabel("log(R/S)")
    plt.title("R/S Plot")
    plt.grid(True)
    plt.legend()
    plt.savefig("rs_plot.png")
    plt.clf()

    # Plot Variance
    var_df = result["var"]
    plt.figure(figsize=(8, 4))
    plt.plot(var_df["log_m"], var_df["log_var"], "o-", color="orange", label="Variance")
    plt.xlabel("log(m)")
    plt.ylabel("log(Variance)")
    plt.title("Variance-Time Plot")
    plt.grid(True)
    plt.legend()
    plt.savefig("variance_plot.png")
    plt.clf()

    # Periodogram
    periodogram_df = result["periodogram"]
    plt.figure(figsize=(8, 4))
    plt.plot(
        periodogram_df["log_freq"],
        periodogram_df["log_power"],
        ".",
        label="Periodogram",
    )
    plt.xlabel("log(Frequency)")
    plt.ylabel("log(Power)")
    plt.title("Periodogram")
    plt.grid(True)
    plt.legend()
    plt.savefig("periodogram_plot.png")
    plt.clf()

    # Plot Hurst estimate vs aggregation level
    hurst_df = result["hurst"]
    print("\nHurst Exponent Estimates:")
    print(hurst_df)

    plt.figure(figsize=(8, 4))

    # R/S and Variance are related to aggregation level
    plt.axhline(
        y=hurst_df.loc[hurst_df["method"] == "rs", "hurst"].values[0],
        color="b",
        linestyle="--",
        label="R/S Estimate",
    )
    plt.axhline(
        y=hurst_df.loc[hurst_df["method"] == "var", "hurst"].values[0],
        color="orange",
        linestyle="--",
        label="Variance Estimate",
    )

    # Spectral estimate as horizontal line
    plt.axhline(
        y=hurst_df.loc[hurst_df["method"] == "spec", "hurst"].values[0],
        color="green",
        linestyle="--",
        label="Spectral Estimate",
    )

    plt.xlabel("Aggregation level (m)")
    plt.ylabel("Estimated Hurst Exponent")
    plt.title("Hurst Exponent Estimates")
    plt.grid(True)
    plt.legend()
    plt.savefig("hurst_estimates.png")
    plt.clf()


if __name__ == "__main__":
    calc_self_similarity_stats_as_df(None)
    # test_calc_self_similarity_stats_as_df()
