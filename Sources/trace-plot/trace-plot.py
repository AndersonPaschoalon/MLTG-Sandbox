from Plotter import TracePlotter


plt1 = TracePlotter(plot_color='red', trace_id='1', flow_database_file="db/TestSkype_Flow.db")
plt_list = []
plt_list.append(plt1)

TracePlotter.plot_bandwidth(plt_list)
TracePlotter.plot_wavelet_multiresolution_energy_analysis_pps(plt_list)
