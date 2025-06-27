import numpy as np
import pandas as pd
import pywt

from commons.connectors.alchemy_connector import AlchemyConnector
from trace_analyzer.metrics.packet_level import get_packet_arrival_df


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
