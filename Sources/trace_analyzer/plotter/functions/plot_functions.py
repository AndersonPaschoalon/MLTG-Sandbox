from typing import Dict, List, Tuple

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pandas import DataFrame
from scipy.stats import linregress


def save_figure(path: str, dpi: int = 300):
    plt.tight_layout()
    plt.savefig(path, dpi=dpi)
    plt.close()


def plot_cdf(
    df_map, column, xlabel, title, save_path_base, log_scale=False
) -> Tuple[str, str]:
    plt.figure(figsize=(10, 6))
    for label, df in df_map.items():
        values = df[column].dropna().values
        values = np.sort(values)
        cdf = np.arange(len(values)) / len(values)
        plt.plot(values, cdf, label=label)

    plt.xlabel(xlabel)
    plt.ylabel("CDF")
    plt.title(title)
    if log_scale:
        plt.xscale("log")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    png_file = f"{save_path_base}.png"
    plt.savefig(png_file)
    plt.close()

    # Save raw CDF data
    csv_file = f"{save_path_base}.csv"
    with open(csv_file, "w") as f:
        f.write("label,value,cdf\n")
        for label, df in df_map.items():
            values = df[column].dropna().values
            values = np.sort(values)
            cdf = np.arange(len(values)) / len(values)
            for v, c in zip(values, cdf):
                f.write(f"{label},{v},{c}\n")

    return png_file, csv_file


def plot_line(
    df_map, x_col, y_col, xlabel, ylabel, title, save_path_base, log_y=False
) -> str:
    plt.figure(figsize=(10, 6))
    for label, df in df_map.items():
        plt.plot(df[x_col], df[y_col], label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if log_y:
        plt.yscale("log")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    png_file = f"{save_path_base}.png"
    plt.savefig(png_file)
    plt.close()
    return png_file


def plot_distribution_plot(
    df_map,
    column,
    title,
    xlabel,
    ylabel,
    save_path_base,
    plot_kind="violin",  # "box" or "violin"
    log_y=True,
) -> Tuple[str, str]:
    """
    Generate a distribution plot (violin or box) comparing a numerical column across multiple datasets.

    Parameters
    ----------
    df_map : dict[str, pd.DataFrame]
        A dictionary where each key is a label (target name) and each value is a pandas DataFrame
        containing the data for that target. Each DataFrame must contain the `column` specified.
        For example, this can represent multiple network trace results from different tools or configurations.

    column : str
        The name of the numerical column to be plotted from each DataFrame in `df_map`.
        This column is expected to contain continuous values (e.g., packet size, latency).

    title : str
        Title of the resulting plot.

    xlabel : str
        Label for the x-axis, usually representing the target (e.g., tool or method name).

    ylabel : str
        Label for the y-axis, usually representing the variable being compared (e.g., "Latency (ms)").

    save_path_base : str
        Base path for saving the output files. A `.png` image and a `.csv` with statistics
        will be saved using this base path (e.g., "plots/latency_comparison" → saves
        "plots/latency_comparison.png" and "plots/latency_comparison.csv").

    plot_kind : str, optional
        Type of plot to generate: "violin" (default) or "box".

    log_y : bool, optional
        Whether to use a logarithmic scale for the y-axis. Useful for skewed distributions.
        Default is True.

    Output
    ------
    Saves a plot as a PNG and summary statistics (mean and std per group) as a CSV.
    """
    assert plot_kind in ("violin", "box"), "Invalid plot kind. Use 'box' or 'violin'."

    # Prepare DataFrame for seaborn
    data_all = []
    labels = []
    stats_records = []

    for label, df in df_map.items():
        series = df[column].dropna()
        data_all.extend(series)
        labels.extend([label] * len(series))
        stats_records.append(
            {"target": label, "mean": series.mean(), "std": series.std()}
        )

    df_plot = pd.DataFrame({"value": data_all, "target": labels})

    plt.figure(figsize=(10, 6))
    if plot_kind == "violin":
        sns.violinplot(x="target", y="value", data=df_plot, inner="box", cut=0)
    else:
        sns.boxplot(x="target", y="value", data=df_plot)

    if log_y:
        plt.yscale("log")

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Annotate mean ± std
    for i, record in enumerate(stats_records):
        mean_val = record["mean"]
        std_val = record["std"]
        group_df = df_plot[df_plot["target"] == record["target"]]
        y_pos = group_df["value"].max() * 1.05
        plt.text(
            i,
            y_pos,
            f"μ={mean_val:.2e}\nσ={std_val:.2e}",
            ha="center",
            va="bottom",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=1),
        )

    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    file_png = f"{save_path_base}.png"
    plt.savefig(file_png)
    plt.close()

    # Save stats to CSV
    csv_file = f"{save_path_base}.csv"
    pd.DataFrame(stats_records).to_csv(csv_file, index=False)
    return file_png, csv_file


def plot_pdf(
    df_map,
    column,
    title,
    xlabel,
    ylabel,
    save_path_base,
    log_y=False,
    log_x=False,
):
    """
    Plot probability density function (PDF) for a given column across multiple targets.

    Parameters:
        df_map (dict[str, pd.DataFrame]): Maps target name to DataFrame.
        column (str): Column name to plot density for.
        title (str): Plot title.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        save_path_base (str): Base path for saving output files (no extension).
        log_y (bool): Whether to use logarithmic scale on Y-axis.
        log_x (bool): Whether to use logarithmic scale on X-axis.
    """
    plt.figure(figsize=(10, 6))

    for label, df in df_map.items():
        series = df[column].dropna()
        if series.empty:
            continue

        sns.kdeplot(series, label=label, linewidth=2)

    if log_y:
        plt.yscale("log")
    if log_x:
        plt.xscale("log")

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    filename = f"{save_path_base}.png"
    plt.savefig(filename)
    plt.close()
    return filename


def plot_timeseries(
    df_map,
    x_col,
    y_cols,
    title,
    xlabel,
    ylabel,
    save_path_base,
    time_max=None,
):
    """
    Plot time series for multiple targets with optional truncation.

    Parameters:
    - df_map: dict of {label: DataFrame}
    - x_col: column name for X-axis (usually "time")
    - y_cols: list of tuples like [(col_name, label_suffix, linewidth)]
    - title: plot title
    - xlabel: X-axis label
    - ylabel: Y-axis label
    - save_path_base: output base name (for .png and .csv)
    - time_max: truncate X at this max value (e.g., shared max time)
    """
    plt.figure(figsize=(10, 6))
    colors = cm.get_cmap("tab10")

    for i, (label, df) in enumerate(df_map.items()):
        df_plot = df[df[x_col] <= time_max] if time_max else df
        color = colors(i % 10)
        for col_name, suffix, lw in y_cols:
            plt.plot(
                df_plot[x_col],
                df_plot[col_name],
                label=f"{label} ({suffix})",
                linewidth=lw,
                color=color,
            )

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    filename = f"{save_path_base}.png"
    plt.savefig(filename)
    plt.close()
    return filename


def plot_histogram(df, column, title, xlabel, ylabel, save_path, color="blue", bins=30):
    """
    Plot and save a histogram for a single time-series column.
    """
    plt.figure(figsize=(10, 6))
    plt.hist(df[column].dropna(), bins=bins, alpha=0.75, edgecolor="black", color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    filename = f"{save_path}.png"
    plt.savefig(filename)
    plt.close()
    return filename


def plot_multiline_metric(
    df_map,
    x_column: str,
    y_column: str,
    title: str = "Multiline Metric Plot",
    xlabel: str = "X-axis",
    ylabel: str = "Y-axis",
    save_path_base: str = "multiline_metric_plot",
) -> str:
    """
    Plot multiple lines from a dictionary of DataFrames with distinct colors.

    This function is generic and can be used for plotting any X vs Y metrics
    across multiple targets (e.g., wavelet energy, time series comparisons, etc.).

    Parameters:
        df_map (dict[str, pd.DataFrame]): Mapping from target name to DataFrame.
        x_column (str): Column name for X-axis.
        y_column (str): Column name for Y-axis.
        title (str): Title for the plot.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        save_path_base (str): Base path to save the plot (without extension).

    Returns:
        str: The filename of the saved plot.
    """
    plt.figure(figsize=(10, 6))
    colors = cm.get_cmap("tab10")

    for idx, (label, df) in enumerate(df_map.items()):
        color = colors(idx % 10)
        plt.plot(df[x_column], df[y_column], label=label, linewidth=2, color=color)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()

    png_file = f"{save_path_base}.png"
    plt.savefig(png_file)
    plt.close()

    return png_file


def plot_single_rs_analysis(
    df, title="R/S Analysis", save_path_base="rs_analysis_plot"
) -> str:
    plt.figure(figsize=(8, 6))

    # Scatter all R/S data points
    plt.scatter(
        df["log10_block_size"],
        df["log10_rs"],
        s=15,
        marker="+",
        label="R/S values",
        alpha=0.6,
    )

    # Reference lines from origin
    x = np.linspace(df["log10_block_size"].min(), df["log10_block_size"].max(), 100)
    plt.plot(x, x * 1.0, "--", color="gray", label="H = 1.0 (Brownian)")
    plt.plot(x, x * 0.5, "--", color="black", label="H = 0.5 (White Noise)")

    plt.title(title)
    plt.xlabel("log10(Block Size)")
    plt.ylabel("log10(R/S)")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()

    path = f"{save_path_base}.png"
    plt.savefig(path)
    plt.close()
    return path


"""
def plot_variance_time_cloud__(
    df, save_path_base="variance_time_plot", title="Variance-Time Plot"
):
    if "aggregation_level" not in df.columns or df.empty:
        raise ValueError("Expected column 'aggregation_level' missing or empty.")

    df = df.copy()
    df["log10_m"] = np.log10(df["aggregation_level"])

    # --- Fit line ---
    slope, intercept, _, _, _ = linregress(df["log10_m"], df["log10_variance"])
    df["fitted_line"] = df["log10_m"] * slope + intercept
    df["line_-1"] = df["log10_m"] * (-1) + intercept  # Reference slope -1

    plt.figure(figsize=(10, 6))
    plt.scatter(df["log10_m"], df["log10_variance"], s=40, marker="+", label="Variance")

    # Plot reference line with slope -1
    plt.plot(
        df["log10_m"], df["line_-1"], linestyle="--", color="gray", label="slope = -1"
    )

    # Plot fitted regression line
    plt.plot(
        df["log10_m"],
        df["fitted_line"],
        linestyle="-",
        color="black",
        label=f"fit: slope={slope:.2f}",
    )

    plt.title(title)
    plt.xlabel("log10(m)")
    plt.ylabel("log10(variances)")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()

    filename = f"{save_path_base}.png"
    plt.savefig(filename)
    plt.close()
    return filename
"""


def plot_variance_time_cloud(
    df,
    save_path_base: str = "variance_time_plot",
    title: str = "Variance-Time Plot",
) -> str:
    if df.empty or "log10_block_size" not in df or "log10_variance" not in df:
        raise ValueError(
            "Expected columns 'log10_block_size' and 'log10_variance' are missing or empty."
        )

    df = df.copy()

    # --- Fit regression line ---
    slope, intercept, _, _, _ = linregress(df["log10_block_size"], df["log10_variance"])
    df["fitted_line"] = df["log10_block_size"] * slope + intercept
    df["line_-1"] = (
        df["log10_block_size"] * (-1) + intercept
    )  # Reference line slope = -1

    plt.figure(figsize=(10, 6))
    plt.scatter(
        df["log10_block_size"],
        df["log10_variance"],
        s=40,
        marker="+",
        alpha=0.7,
        label="Normalized Variance",
    )

    # Plot slope = -1 reference
    plt.plot(
        df["log10_block_size"],
        df["line_-1"],
        linestyle="--",
        color="gray",
        label="Reference: slope = -1",
    )

    # Plot fitted line
    plt.plot(
        df["log10_block_size"],
        df["fitted_line"],
        linestyle="-",
        color="black",
        label=f"Fitted slope = {slope:.2f}",
    )

    plt.title(title)
    plt.xlabel("log10(Block Size m)")
    plt.ylabel("log10(Normalized Variance)")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()

    filename = f"{save_path_base}.png"
    plt.savefig(filename, dpi=300)
    plt.close()
    print("-------------------")
    return filename


def plot_scatter(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    xlabel: str,
    ylabel: str,
    title: str,
    save_path_base: str,
    loglog: bool = False,
) -> str:
    """
    Plot a scatter plot from a single DataFrame and save both PNG and CSV files.

    Args:
        df (pd.DataFrame): Data to be plotted.
        x_column (str): Column name for X-axis.
        y_column (str): Column name for Y-axis.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        title (str): Plot title.
        save_path_base (str): Path prefix for saving the plot and CSV (no extension).
        loglog (bool): Whether to apply log-log scaling.

    Returns:
        str: Filename of the saved plot.
    """
    if df.empty:
        raise ValueError("DataFrame is empty. Nothing to plot.")

    plt.figure(figsize=(10, 6))
    plt.scatter(df[x_column], df[y_column], s=40, marker="+", label=title)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle="--", linewidth=0.5)

    if loglog:
        plt.xscale("log")
        plt.yscale("log")

    plt.tight_layout()

    png_file = f"{save_path_base}.png"
    plt.savefig(png_file)
    plt.close()

    csv_file = f"{save_path_base}.csv"
    df.to_csv(csv_file, index=False)

    return png_file


def plot_correlogram(
    df: pd.DataFrame,
    xlabel: str,
    ylabel: str,
    title: str,
    save_path_base: str,
) -> List[str]:
    """
    Plots a correlogram from lag-autocorrelation data.

    Args:
        df: DataFrame with 'lag' and 'autocorrelation' columns.
        xlabel: Label for x-axis.
        ylabel: Label for y-axis.
        title: Plot title.
        save_path_base: File path base (without extension).

    Returns:
        List with paths to saved files: [png_file, csv_file]
    """
    if df.empty:
        print(f"[WARN] Empty dataframe for {title} — skipping plot.")
        return []

    plt.figure(figsize=(10, 6))
    plt.stem(df["lag"], df["autocorrelation"], basefmt=" ")

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()

    png_file = f"{save_path_base}.png"
    plt.savefig(png_file)
    plt.close()

    csv_file = f"{save_path_base}.csv"
    df.to_csv(csv_file, index=False)

    return png_file


def plot_lines(
    df_map: Dict[str, pd.DataFrame],
    x_column: str,
    y_column: str,
    xlabel: str,
    ylabel: str,
    title: str,
    save_path_base: str,
    x_axis_logscale: bool = False,
    y_axis_logscale: bool = False,
) -> List[str]:
    """
    Plots a multi-line chart from a dictionary of target → DataFrame.

    Args:
        df_map: Dict of {label: DataFrame}
        x_column: Column name to use for X-axis
        y_column: Column name to use for Y-axis
        xlabel: X-axis label
        ylabel: Y-axis label
        title: Plot title
        save_path_base: Path base to save PNG and CSV (no extension)

    Returns:
        List with paths to saved file png_file
    """
    if not df_map:
        print(f"[WARN] No data provided for '{title}' — skipping plot.")
        return []

    plt.figure(figsize=(10, 6))

    for label, df in df_map.items():
        if df.empty or x_column not in df.columns or y_column not in df.columns:
            print(f"[WARN] Skipping '{label}' — required columns missing or empty.")
            continue

        x = df[x_column].dropna()
        y = df[y_column].dropna()
        if len(x) != len(y):
            print(f"[WARN] Skipping '{label}' — X and Y column size mismatch.")
            continue

        plt.plot(x, y, label=label)

    if x_axis_logscale:
        plt.xscale("log")
    if y_axis_logscale:
        plt.yscale("log")

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()

    png_file = f"{save_path_base}.png"
    plt.savefig(png_file, dpi=300)
    plt.close()

    # Save combined CSV with "label" column
    csv_file = f"{save_path_base}.csv"
    with open(csv_file, "w") as f:
        f.write(f"label,{x_column},{y_column}\n")
        for label, df in df_map.items():
            if df.empty or x_column not in df or y_column not in df:
                continue
            for x, y in zip(df[x_column], df[y_column]):
                f.write(f"{label},{x},{y}\n")

    return png_file
