import os
from Plotter import Plotter
from PlotData import  PlotData


out_dir = os.path.join("plots/test01")
data1 = PlotData(flow_database="random", name="data-01", color="blue")
data2 = PlotData(flow_database="random", name="data-02", color="red")
plot_list = [data1, data2]
Plotter.plot_interarrival_cdf(plot_data_list=plot_list, out_dir=out_dir)
Plotter.plot_interarrival_time_distribution(plot_data_list=plot_list, out_dir=out_dir)
Plotter.plot_iplot_bandwidth_mbps(plot_data_list=plot_list, out_dir=out_dir)
