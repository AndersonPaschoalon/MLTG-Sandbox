def plot_variance_time(var_df, filename="variance_time_plot.png"):
    """
    Plot the variance-time plot: log2(Var(X_m)) vs log2(m).

    Args:
        var_df (pd.DataFrame): DataFrame returned from self_similarity_variance()[1]
        filename (str): Name of the output plot file
    """
    plt.figure(figsize=(8, 5))

    # Main line: actual variance values
    plt.plot(
        var_df["log_m"],
        var_df["log_var"],
        marker="o",
        linestyle="-",
        label="log(Variance)",
        color="blue",
    )

    # Reference slope = -1 (ideal memoryless behavior)
    plt.plot(
        var_df["log_m"],
        var_df["ref_slope_-1"],
        linestyle="--",
        color="gray",
        label="slope = -1 (ref)",
    )

    # Labels and title
    plt.xlabel("log2(m)")
    plt.ylabel("log2(Variance)")
    plt.title("Variance-Time Plot")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def self_similarity_variance_time(
    ac=None, flowID=0, aggregation_levels=[1, 5, 10, 50, 100, 500]
):
    def _variance_time_analysis(series, block_sizes):
        log_ms, log_vars = [], []

        for m in block_sizes:
            if m >= len(series):
                continue

            step = max(1, m // 4)
            chunk_means = []

            for start in range(0, len(series) - m + 1, step):
                block = series[start : start + m]
                chunk_means.append(np.mean(block))

            if len(chunk_means) > 1:
                var = np.var(chunk_means, ddof=1)
                log_ms.append(np.log2(m))
                log_vars.append(np.log2(var))

        var_df = pd.DataFrame({"log_m": log_ms, "log_var": log_vars})

        if not var_df.empty:
            slope, _, _, _, _ = linregress(var_df["log_m"], var_df["log_var"])
            hurst = 1 - slope / 2
        else:
            slope = hurst = np.nan

        return var_df, hurst

    # --- Load data ---
    if ac is None:
        df = _generate_synthetic_interarrival_df()
    else:
        df = get_packet_arrival_df(ac, flowID=flowID)

    # Bin into 10ms intervals
    bin_width = 0.01
    time_start = df["timestamp"].min()
    time_end = df["timestamp"].max()
    bins = np.arange(time_start, time_end + bin_width, bin_width)
    df["time_bin"] = pd.cut(df["timestamp"], bins=bins, labels=False)
    bytes_per_bin = df.groupby("time_bin")["pkt_size"].sum().fillna(0).values

    # --- Variance-Time Analysis (like Figure 2b) ---
    var_df, _ = _variance_time_analysis(
        bytes_per_bin, block_sizes=[2, 4, 8, 16, 32, 64, 128]
    )
    x = var_df["log_m"]
    var_df["ref_slope_-1"] = -1.0 * x

    # --- Hurst vs Aggregation Level ---
    hurst_vs_m = []
    var_ag = []
    for m in aggregation_levels:
        n = len(bytes_per_bin) // m
        truncated = bytes_per_bin[: n * m]
        agg_series = truncated.reshape((n, m)).mean(axis=1)
        v, hurst = _variance_time_analysis(agg_series, block_sizes=[2, 4, 8, 16, 32])
        hurst_vs_m.append((m, hurst))
        var_ag.append({"m": m, "var": v})

    hurst_df = pd.DataFrame(hurst_vs_m, columns=["aggregation_level", "hurst_var"])
    return hurst_df, var_df, var_ag


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
