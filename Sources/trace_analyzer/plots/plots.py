from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


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
    target_list=None,
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
        target_list (list[str], optional): If provided, only plots these targets.
        log_y (bool): Whether to use logarithmic scale on Y-axis.
        log_x (bool): Whether to use logarithmic scale on X-axis.
    """
    target_list = target_list or []

    plt.figure(figsize=(10, 6))

    for label, df in df_map.items():
        if target_list and label not in target_list:
            continue

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
    plt.savefig(f"{save_path_base}.png")
    plt.close()


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
    import matplotlib.cm as cm
    import matplotlib.pyplot as plt

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
    plt.savefig(f"{save_path_base}.png")
    plt.close()


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
    plt.savefig(f"{save_path}.png")
    plt.close()
