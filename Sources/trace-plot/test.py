import os
from Plotter import Plotter
from PlotData import  PlotData


out_dir = os.path.join("plots/test01")
data1 = PlotData(flow_database="random", name="data-01", color="blue")
data2 = PlotData(flow_database="random", name="data-02", color="red")
plot_list = [data1, data2]
Plotter.plot_interarrival_cdf(plot_data_list=plot_list, out_dir=out_dir)
Plotter.plot_interarrival_time_distribution(plot_data_list=plot_list, out_dir=out_dir)
Plotter.plot_bandwidth_mbps(plot_data_list=[data1], out_dir=out_dir)


data3 = PlotData(flow_database="random2a", name="data-01", color="blue")
data4 = PlotData(flow_database="random2b", name="data-02", color="red")
Plotter.plot_wavelet_multiresolution_energy(plot_data_list=[data3, data4], out_dir=out_dir)
Plotter.plot_bandwidth_mbps(plot_data_list=[data3], out_dir=out_dir, nickname="data03")



