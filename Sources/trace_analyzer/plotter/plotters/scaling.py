import logging

import matplotlib.cm as cm

import trace_analyzer.core.data_loader as data_loader
import trace_analyzer.plotter.functions.plot_functions as plot_functions
from commons.logger.logger import Logger
from trace_analyzer.core.state import get_env, get_mem

env = get_env()
mem = get_mem()


def plot_wavelet_multiresolution_energy_analysis(target_list=None):
    """
    Plots Multiresolution Energy analysis!
    wavelet_df_map
    """
    df_map = data_loader.filter_df_map_by_target(mem.wavelet_df_map, target_list)
    filename = mem.pnf.mkname("wavelet-mea", list(df_map.keys()))
    plot_functions.plot_multiline_metric(
        df_map=df_map,
        x_column="scale",
        y_column="log2_energy",
        title="Wavelet Energy Comparison",
        xlabel="Time Scale j",
        ylabel="log2(Energy(j))",
        save_path_base=filename,
    )


def plot_rs_analysis_by_target(target_list=None):
    """
    Plot R/S analysis curves per target.

    This function will plot one figure per target, each showing the R/S curve
    and the slope reference lines (1.0 and 0.5).
    """
    df_map = data_loader.filter_df_map_by_target(mem.hurst_rs_df_map, target_list)

    saved_files = []
    for label, df in df_map.items():
        filename = mem.pnf.mkname("rs-analysis", [label])
        out_file = plot_functions.plot_single_rs_analysis(
            df=df, title=f"R/S Analysis - {label}", save_path_base=filename
        )
        saved_files.append(out_file)

    return saved_files


def plot_variance_time_analysis(target_list=None):
    df_map = data_loader.filter_df_map_by_target(
        mem.hurst_variancetime_df_map, target_list
    )

    saved_files = []
    for label, df in df_map.items():
        filename = mem.pnf.mkname("hurst_variancetime", [label])
        out_file = plot_functions.plot_variance_time_cloud(
            df=df,
            save_path_base=filename,
            title=f"Variance-Time Analysis - {label}",
        )
        saved_files.append(out_file)

    return saved_files
