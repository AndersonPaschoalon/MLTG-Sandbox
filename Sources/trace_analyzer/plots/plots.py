import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot_cdf(df_map, column, xlabel, title, save_path_base, log_scale=False):
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
    plt.savefig(f"{save_path_base}.png")
    plt.close()

    # Save raw CDF data
    with open(f"{save_path_base}.csv", "w") as f:
        f.write("label,value,cdf\n")
        for label, df in df_map.items():
            values = df[column].dropna().values
            values = np.sort(values)
            cdf = np.arange(len(values)) / len(values)
            for v, c in zip(values, cdf):
                f.write(f"{label},{v},{c}\n")


def plot_line(df_map, x_col, y_col, xlabel, ylabel, title, save_path_base, log_y=False):
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
    plt.savefig(f"{save_path_base}.png")
    plt.close()
