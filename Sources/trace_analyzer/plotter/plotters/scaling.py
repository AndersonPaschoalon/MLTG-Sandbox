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
