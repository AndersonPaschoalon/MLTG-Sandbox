import numpy as np
import pandas as pd
import pywt
from scipy.signal import periodogram
from scipy.stats import linregress
from statsmodels.tsa.stattools import acf

import trace_analyzer.metrics.packet_level as packet_level
from commons.connectors.alchemy_connector import AlchemyConnector


def calc_wavelet_as_df(
    ac: AlchemyConnector,
    flowID: int = 0,
    wavelet: str = "db4",
    level: int = 5,
) -> pd.DataFrame:
    """
    Perform WMEA using timestamp binning from SnifyLite DB.

    Args:
        ac (AlchemyConnector): Active database connector.
        flowID (int): Specific flow to analyze. Default is 0 (all).
        wavelet (str): Wavelet type.
        level (int): Decomposition level.

    Returns:
        pd.DataFrame: DataFrame with scale, log2_energy, and target.
    """
    signal = packet_level.get_bandwidth_signal(
        ac=ac, flowID=flowID, bin_width=0.01, agg="sum"
    )

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

    df["hurst_estimate"] = 1 - abs(slope)  # For variance-time: H = 1 - slope
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
    agg: str = "sum",
    min_block_size: int = 10,
    max_block_size_cap: int = 1000,
) -> pd.DataFrame:
    signal = packet_level.get_bandwidth_signal(
        ac=ac, flowID=flowID, bin_width=0.01, agg="count"
    )

    all_results = []
    for m in aggregation_levels:
        if m >= len(signal):
            continue

        k = len(signal) // m
        truncated = signal[: k * m]
        aggregated = truncated.reshape((k, m)).sum(axis=1)

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
    min_block_size: int = 10,
    max_block_size_cap: int = 1000,
) -> pd.DataFrame:

    signal = packet_level.get_bandwidth_signal(
        ac=ac, flowID=flowID, bin_width=0.01, agg="sum"
    )

    # Perform full variance-time analysis ONCE
    vt_df = _perform_variance_time_analysis(
        signal,
        min_block_size=min_block_size,
        max_block_size=min(max_block_size_cap, len(signal) // 10),
    )

    return vt_df


def _compute_periodogram(signal: np.ndarray, fs: float = 1.0):
    """
    Compute periodogram and return log10(freq), log10(power), and slope fit on low frequencies.
    Returns empty arrays and np.nan if input is too short or invalid.
    """
    freqs, power = periodogram(signal, fs=fs, scaling="density", detrend=False)

    # Avoid log of zero or negative
    mask = (freqs > 0) & np.isfinite(power) & (power > 0)
    freqs = freqs[mask]
    power = power[mask]

    if len(freqs) == 0 or len(power) == 0:
        print("[WARN] Empty frequency or power array after filtering. Skipping.")
        return np.array([]), np.array([]), np.nan

    log_freq = np.log10(freqs)
    log_power = np.log10(power)

    cutoff = int(0.2 * len(log_freq))
    if cutoff == 0:
        print("[WARN] Not enough frequency samples for linear regression. Skipping.")
        return log_freq, log_power, np.nan

    slope, _, _, _, _ = linregress(log_freq[:cutoff], log_power[:cutoff])
    hurst_estimate = (1 - abs(slope)) / 2  # Spectral method

    return log_freq, log_power, hurst_estimate


def calc_periodogram_as_df(
    ac,
    flowID: int = 0,
    aggregation_levels: list = [1, 5, 10, 50, 100, 500, 1000],
    base_bin_width: float = 0.01,  # T0 = 10ms
) -> pd.DataFrame:
    """
    Calculate periodogram for different aggregation levels (m * T0).
    Each result is tagged with m and its corresponding Hurst exponent estimate.
    Returns a single stacked DataFrame.
    """
    raw_signal = packet_level.get_bandwidth_signal(
        ac=ac, flowID=flowID, bin_width=base_bin_width, agg="sum"
    )

    results = []
    for m in aggregation_levels:
        if m >= len(raw_signal):
            continue

        k = len(raw_signal) // m
        truncated = raw_signal[: k * m]
        aggregated = truncated.reshape((k, m)).sum(axis=1)

        try:
            log_freq, log_power, hurst = _compute_periodogram(aggregated, fs=1.0)
            if len(log_freq) == 0 or len(log_power) == 0:
                continue

            df = pd.DataFrame(
                {
                    "log10_frequency": log_freq,
                    "log10_power": log_power,
                    "aggregation_level": m,
                    "hurst_estimate": hurst,
                }
            )
            results.append(df)
        except Exception as e:
            print(f"[ERROR] Failed to compute periodogram for m={m}: {e}")

    if results:
        return pd.concat(results, ignore_index=True)
    else:
        return pd.DataFrame(
            columns=[
                "log10_frequency",
                "log10_power",
                "aggregation_level",
                "hurst_estimate",
            ]
        )


def calc_interarrival_correlogram(
    ac,
    flowID: int = 0,
    max_lag: int = 50,
    nlags: int = 50,
) -> pd.DataFrame:
    """
    Computes the autocorrelation (correlogram) of interarrival times for a flow.

    Args:
        ac: AlchemyConnector
        flowID: Target flow ID
        max_lag: Max lag to compute ACF
        nlags: Number of lags in ACF (used if max_lag not specified)

    Returns:
        pd.DataFrame with columns: 'lag', 'autocorrelation'
    """
    df = packet_level.get_packet_arrival_df(ac, flowID=flowID)
    interarrivals = df["inter_arrival"].dropna().values

    if len(interarrivals) < 10:
        return pd.DataFrame()  # Not enough data

    acf_vals = acf(interarrivals, nlags=max_lag, fft=True)

    return pd.DataFrame({"lag": np.arange(len(acf_vals)), "autocorrelation": acf_vals})


def calc_idc_per_timescale_as_df(
    ac,
    flowID: int = 0,
    time_scales: list = [0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, 200],
) -> pd.DataFrame:
    """
    Calculates the Index of Dispersion for Counts (IDC) over multiple time scales.

    Returns:
        DataFrame with columns:
            - time_scale
            - idc
            - log10_idc
    """
    results = []

    for scale in time_scales:
        print(f"[INFO] Processing time scale: {scale} s")

        signal = packet_level.get_bandwidth_signal(
            ac=ac, flowID=flowID, bin_width=scale, agg="count"
        )

        if signal is None or len(signal) == 0:
            print(f"[WARN] Empty signal for scale {scale}, skipping.")
            continue

        values = np.asarray(signal)
        values = values[~np.isnan(values)]  # remove NaNs if any

        if len(values) == 0:
            print(f"[WARN] All-NaN signal for scale {scale}, skipping.")
            continue

        mean_val = np.mean(values)
        var_val = np.var(values)

        if mean_val > 0:
            idc = var_val / mean_val
            log_idc = np.log10(idc)
            results.append({"time_scale": scale, "idc": idc, "log10_idc": log_idc})

    return pd.DataFrame(results)
