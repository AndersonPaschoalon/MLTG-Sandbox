import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from commons.connectors.alchemy_connector import AlchemyConnector
from trace_analyzer.metrics.packet_level import get_packet_arrival_df


def _calc_burst_metrics(ac: AlchemyConnector, inter_arrival_threshold=0.01):
    # Analyze bursts for a given target and DB connector.
    # - Burst: sequence of packets where inter-arrival < threshold.

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


def calc_burst_metrics_base(ac: AlchemyConnector, inter_arrival_threshold=0.01):
    """
    Common base function for burst analysis.
    Returns a dictionary with all burst data for further processing.
    """
    print(f"[burst] Analyzing bursts with threshold {inter_arrival_threshold}")

    df = get_packet_arrival_df(ac).sort_values("time").reset_index(drop=True)

    if df.empty or len(df) < 2:
        print(f"[WARN] Not enough packets for burst analysis")
        return None

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
    burst_data = {
        "sizes": [len(b) for b in bursts],
        "durations": [b["time"].iloc[-1] - b["time"].iloc[0] for b in bursts],
        "intervals": (
            [
                bursts[i]["time"].iloc[0] - bursts[i - 1]["time"].iloc[-1]
                for i in range(1, len(bursts))
            ]
            if len(bursts) > 1
            else []
        ),
    }

    # Filter valid values
    burst_data["sizes"] = [x for x in burst_data["sizes"] if x > 0 and np.isfinite(x)]
    burst_data["durations"] = [
        x for x in burst_data["durations"] if x > 0 and np.isfinite(x)
    ]
    burst_data["intervals"] = [
        x for x in burst_data["intervals"] if x > 0 and np.isfinite(x)
    ]

    return burst_data


def calc_burst_sizes_as_df(
    ac: AlchemyConnector, inter_arrival_threshold=0.01
) -> pd.DataFrame:
    """Returns DataFrame with burst sizes"""
    burst_data = calc_burst_metrics_base(ac, inter_arrival_threshold)
    if not burst_data:
        return pd.DataFrame(columns=["burst_size"])
    return pd.DataFrame({"burst_size": burst_data["sizes"]})


def calc_burst_durations_as_df(
    ac: AlchemyConnector, inter_arrival_threshold=0.01
) -> pd.DataFrame:
    """Returns DataFrame with burst durations"""
    burst_data = calc_burst_metrics_base(ac, inter_arrival_threshold)
    if not burst_data:
        return pd.DataFrame(columns=["burst_duration"])
    return pd.DataFrame({"burst_duration": burst_data["durations"]})


def calc_burst_intervals_as_df(
    ac: AlchemyConnector, inter_arrival_threshold=0.01
) -> pd.DataFrame:
    """Returns DataFrame with inter-burst intervals"""
    burst_data = calc_burst_metrics_base(ac, inter_arrival_threshold)
    if not burst_data:
        return pd.DataFrame(columns=["burst_interval"])
    return pd.DataFrame({"burst_interval": burst_data["intervals"]})
