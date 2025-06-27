import logging

import matplotlib.cm as cm

import trace_analyzer.core.data_loader as data_loader
import trace_analyzer.plotter.functions.plot_functions as plot_functions
from commons.logger.logger import Logger
from trace_analyzer.core.state import get_env, get_mem

env = get_env()
mem = get_mem()
