import numpy as np
import pandas as pd
import pywt
from scipy.stats import linregress

from commons.connectors.alchemy_connector import AlchemyConnector
from trace_analyzer.metrics.packet_level import (
    _generate_synthetic_interarrival_df,
    get_packet_arrival_df,
)


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


def _perform_rs_analysis_dense(
    time_series: np.ndarray,
    min_block_size: int = 10,
    max_block_size: int = 1000,
    step_frac: float = 0.25,
) -> pd.DataFrame:
    log_block_sizes = []
    log_rs_values = []

    for d in range(min_block_size, max_block_size + 1):
        if d >= len(time_series):
            continue

        step = max(1, int(d * step_frac))
        rs_vals = []

        for start in range(0, len(time_series) - d + 1, step):
            block = time_series[start : start + d]
            dev = block - np.mean(block)
            cum_dev = np.cumsum(dev)
            R = np.max(cum_dev) - np.min(cum_dev)
            S = np.std(block, ddof=1)
            if S > 0:
                rs_vals.append(R / S)

        if rs_vals:
            avg_rs = np.mean(rs_vals)
            log_block_sizes.append(np.log10(d))
            log_rs_values.append(np.log10(avg_rs))

    rs_df = pd.DataFrame(
        {
            "log10_block_size": log_block_sizes,
            "log10_rs": log_rs_values,
        }
    )

    if not rs_df.empty:
        slope, _, _, _, _ = linregress(rs_df["log10_block_size"], rs_df["log10_rs"])
        rs_df["hurst_estimate"] = slope
    else:
        rs_df["hurst_estimate"] = np.nan

    return rs_df


def _perform_variance_time_analysis(
    time_series: np.ndarray,
    min_block_size: int = 10,
    max_block_size: int = 1000,
    num_points: int = 20,
) -> pd.DataFrame:
    if len(time_series) < min_block_size:
        return pd.DataFrame()

    block_sizes = np.unique(
        np.logspace(
            np.log10(min_block_size),
            np.log10(max_block_size),
            num=num_points,
            dtype=int,
        )
    )

    results = []
    for m in block_sizes:
        if m <= 0 or m >= len(time_series):
            continue

        k = len(time_series) // m
        if k == 0:
            continue

        truncated = time_series[: k * m]
        try:
            reshaped = truncated.reshape((k, m))
        except ValueError:
            continue

        means = reshaped.mean(axis=1)
        var = np.var(means)

        if var > 0 and np.isfinite(var):
            results.append(
                {
                    "block_size": m,
                    "log10_block_size": np.log10(m),
                    "log10_variance": np.log10(var),
                }
            )

    df = pd.DataFrame(results)

    if df.empty:
        return df

    # --- Add slope = -1 line and Hurst estimation ---
    slope, intercept, *_ = linregress(df["log10_block_size"], df["log10_variance"])

    df["hurst_estimate"] = 1 - slope  # For variance-time: H = 1 - slope
    df["line_-1"] = df["log10_block_size"] * (-1) + intercept

    return df[
        [
            "block_size",
            "log10_block_size",
            "log10_variance",
            "hurst_estimate",
            "line_-1",
        ]
    ]


def calc_rs_analysis_as_df_dense(
    ac: AlchemyConnector,
    flowID: int = 0,
    aggregation_levels: list = [1, 5, 10, 50, 100, 500, 1000],
    bin_width: float = 0.01,
    agg: str = "count",
    min_block_size: int = 10,
    max_block_size_cap: int = 1000,
) -> pd.DataFrame:

    df = get_packet_arrival_df(ac, flowID=flowID)

    if df.empty:
        raise ValueError("Input DataFrame is empty. Cannot perform R/S analysis.")

    time_start = df["time"].min()
    time_end = df["time"].max()

    bins = np.arange(time_start, time_end + bin_width, bin_width)
    df["time_bin"] = pd.cut(df["time"], bins=bins, labels=False)

    if agg == "count":
        signal = df.groupby("time_bin").size().values
    elif agg == "sum":
        signal = df.groupby("time_bin")["pkt_size"].sum().fillna(0).values
    else:
        raise ValueError("agg must be 'count' or 'sum'")

    signal = signal[np.isfinite(signal)]

    all_results = []
    for m in aggregation_levels:
        if m >= len(signal):
            continue

        k = len(signal) // m
        truncated = signal[: k * m]
        aggregated = truncated.reshape((k, m)).mean(axis=1)

        rs_df = _perform_rs_analysis_dense(
            time_series=aggregated,
            min_block_size=min_block_size,
            max_block_size=min(max_block_size_cap, len(aggregated) // 10),
        )

        if not rs_df.empty:
            rs_df["aggregation_level"] = m
            all_results.append(rs_df)

    return pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()


def calc_variance_time_analysis_as_df(
    ac: AlchemyConnector,
    flowID: int = 0,
    aggregation_levels: list = [1, 5, 10, 50, 100, 500, 1000],
    bin_width: float = 0.01,
    agg: str = "count",
    min_block_size: int = 10,
    max_block_size_cap: int = 1000,
) -> pd.DataFrame:
    df = get_packet_arrival_df(ac, flowID=flowID)
    if df.empty:
        raise ValueError(
            "Input DataFrame is empty. Cannot perform Variance-Time analysis."
        )

    # Time binning
    time_start = df["time"].min()
    time_end = df["time"].max()
    bins = np.arange(time_start, time_end + bin_width, bin_width)
    df["time_bin"] = pd.cut(df["time"], bins=bins, labels=False)

    if agg == "count":
        signal = df.groupby("time_bin").size().values
    elif agg == "sum":
        signal = df.groupby("time_bin")["pkt_size"].sum().fillna(0).values
    else:
        raise ValueError("agg must be 'count' or 'sum'")

    signal = signal[np.isfinite(signal)]

    # Loop over aggregation levels
    all_results = []
    for m in aggregation_levels:
        if m >= len(signal):
            continue
        k = len(signal) // m
        truncated = signal[: k * m]
        aggregated = truncated.reshape((k, m)).mean(axis=1)

        vt_df = _perform_variance_time_analysis(
            aggregated,
            min_block_size=min_block_size,
            max_block_size=min(max_block_size_cap, len(aggregated) // 10),
        )

        if not vt_df.empty:
            vt_df["aggregation_level"] = m
            all_results.append(vt_df)

    return pd.concat(all_results, ignore_index=True)
