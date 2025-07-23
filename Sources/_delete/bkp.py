def _perform_rs_analysis(
    time_series: np.ndarray,
    min_block_size: int = 10,
    max_block_size: int = 1000,
    num_points: int = 20,
) -> pd.DataFrame:
    """
    Perform R/S analysis on any given time series.

    Parameters:
        time_series: Input data (already aggregated if needed)
        min_block_size: Minimum window size for R/S calculation
        max_block_size: Maximum window size
        num_points: Number of log-spaced block sizes

    Returns:
        DataFrame with:
        - log10_block_size: x-axis values
        - log10_rs: y-axis values
        - hurst_estimate: Local H estimate
        - line_1: Reference line (slope=1)
        - line_05: Reference line (slope=0.5)
    """
    block_sizes = np.unique(
        np.logspace(
            np.log10(min_block_size),
            np.log10(max_block_size),
            num=num_points,
            dtype=int,
        )
    )

    results = []
    for d in block_sizes:
        if d >= len(time_series):
            continue

        k = len(time_series) // d
        truncated = time_series[: k * d].reshape((k, d))

        block_rs = []
        for block in truncated:
            mean = np.mean(block)
            dev = block - mean
            cum_dev = np.cumsum(dev)
            R = np.max(cum_dev) - np.min(cum_dev)
            S = np.std(block, ddof=1)
            if S > 0:
                block_rs.append(R / S)

        if block_rs:
            results.append({"block_size": d, "log10_rs": np.log10(np.mean(block_rs))})

    rs_df = pd.DataFrame(results)
    if rs_df.empty:
        return pd.DataFrame()

    # Calculate Hurst estimate
    x = np.log10(rs_df["block_size"])
    y = rs_df["log10_rs"]
    slope, intercept, _, _, _ = linregress(x, y)

    rs_df["log10_block_size"] = x
    rs_df["hurst_estimate"] = slope
    rs_df["line_1"] = x * 1.0 + intercept
    rs_df["line_05"] = x * 0.5 + intercept

    return rs_df


def calc_rs_analysis_as_df(
    ac: AlchemyConnector,
    flow_id: int = 0,
    aggregation_levels: list = [1, 5, 10, 50, 100, 500, 1000],
) -> pd.DataFrame:
    """
    Main function to calculate R/S analysis across aggregation levels.

    Returns:
        DataFrame with all results stacked, containing:
        - aggregation_level: m value used
        - log10_block_size: x-axis for R/S plot
        - log10_rs: y-axis for R/S plot
        - hurst_estimate: H at this aggregation
        - line_1/line_05: Reference lines
    """
    # Load raw data
    df = get_packet_arrival_df(ac, flowID=flow_id)
    bytes_per_bin = df["pkt_size"].resample("10ms").sum().values

    all_results = []
    for m in aggregation_levels:
        if m >= len(bytes_per_bin):
            continue

        # Create aggregated series
        k = len(bytes_per_bin) // m
        aggregated = bytes_per_bin[: k * m].reshape((k, m)).mean(axis=1)

        # Perform R/S analysis on aggregated series
        rs_df = _perform_rs_analysis(
            aggregated,
            min_block_size=10,
            max_block_size=min(1000, len(aggregated) // 10),
        )

        if not rs_df.empty:
            rs_df["aggregation_level"] = m
            all_results.append(rs_df)

    return pd.concat(all_results).reset_index(drop=True)
