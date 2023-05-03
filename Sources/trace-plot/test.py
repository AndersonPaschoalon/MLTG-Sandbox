import os
from Database.RandomData import RandomData
from Database.TraceDatabase import TraceDatabase
from Plotter import Plotter


we1_data = RandomData(database_file="weibull", name="weibull-01", color="blue")
we2_data = RandomData(database_file="exponential", name="exponential-01", color="red")
we3_data = RandomData(database_file="pareto", name="pareto-01", color="purple")

cfg_str1 = '{"seed": 42, "n_packets": 80, "n_flows": 5}'
cfg_str2 = '{"seed": 58943, "n_packets": 130, "n_flows": 5}'
sp1_data = RandomData(database_file="3spikes", name="3spike-01", color="blue", config_str=cfg_str1)
sp2_data = RandomData(database_file="3spikes", name="3spike-01", color="red", config_str=cfg_str2)

out_dir = os.path.join("plots/test01")

plot_list = [we1_data, we2_data, we3_data]
Plotter.plot_interarrival_cdf(plot_data_list=plot_list, out_dir=out_dir)
Plotter.plot_inter_arrival_time_distribution(plot_data_list=plot_list, out_dir=out_dir)
Plotter.plot_bandwidth_mbps(plot_data_list=[we1_data], out_dir=out_dir)

Plotter.plot_wavelet_multiresolution_energy(plot_data_list=[sp1_data, sp2_data], out_dir=out_dir)
Plotter.plot_bandwidth_mbps(plot_data_list=[sp1_data], out_dir=out_dir, nickname="data03")
Plotter.plot_pps(plot_data_list=[sp1_data], out_dir=out_dir, nickname="data03")



