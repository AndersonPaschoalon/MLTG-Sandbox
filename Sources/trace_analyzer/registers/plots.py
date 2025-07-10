import trace_analyzer.plotter.plotters.burstiness as pltbrt
import trace_analyzer.plotter.plotters.packet_level as pltpkt
import trace_analyzer.plotter.plotters.scaling as pltscl
from trace_analyzer.registers.plot_registry import PlotRegistry


def register_all_plotters():
    # Packet-level plots
    PlotRegistry.register(
        "violin_interarrival", "Violin Interarrival", pltpkt.plot_violin_interarrival
    )
    PlotRegistry.register("violin_pkt", "Violin Packet Size", pltpkt.plot_violin_pkt)
    PlotRegistry.register(
        "box_interarrival", "Boxplot Interarrival", pltpkt.plot_box_interarrival
    )
    PlotRegistry.register("box_pkt", "Boxplot Packet Size", pltpkt.plot_box_pkt)
    PlotRegistry.register(
        "interarrival_pdf", "Interarrival PDF", pltpkt.plot_interarrival_pdf
    )
    PlotRegistry.register(
        "interarrival_cdf", "Interarrival CDF", pltpkt.plot_interarrival_cdf
    )
    PlotRegistry.register(
        "interarrival_by_index",
        "Interarrival by Index",
        pltpkt.plot_interarrival_by_index,
    )
    PlotRegistry.register(
        "bw_bandwidth", "Bandwidth Over Time", pltpkt.plot_bw_pps_fps, "bandwidth"
    )
    PlotRegistry.register(
        "bw_pps", "Packets per Second", pltpkt.plot_bw_pps_fps, "packet_per_second"
    )
    PlotRegistry.register(
        "bw_fps", "Flows per Second", pltpkt.plot_bw_pps_fps, "flow_per_second"
    )
    PlotRegistry.register(
        "pkt_hist", "Packet Size Histogram", pltpkt.plot_pktsize_histogram
    )
    PlotRegistry.register("bw_cdf", "Bandwidth CDF", pltpkt.plot_bandwidth_cdf)
    PlotRegistry.register(
        "pkt_load_cdf", "Packet Load CDF", pltpkt.plot_packet_load_cdf
    )
    PlotRegistry.register(
        "payload_cdf", "Payload Size CDF", pltpkt.plot_payload_size_cdf
    )

    # Burst-level plots
    PlotRegistry.register(
        "burst_size_violin", "Burst Size Violin", pltbrt.plot_burst_size_violin
    )
    PlotRegistry.register(
        "inter_burst_cdf",
        "Inter-Burst Interval CDF",
        pltbrt.plot_inter_burst_interval_cdf,
    )
    PlotRegistry.register(
        "burst_duration_violin",
        "Burst Duration Violin",
        pltbrt.plot_burst_duration_violin,
    )

    # Scaling-level plots
    PlotRegistry.register(
        "wavelet_energy",
        "Wavelet Multiresolution Energy",
        pltscl.plot_wavelet_multiresolution_energy_analysis,
    )
    PlotRegistry.register(
        "hurst_rs_analysis", "R/S Analysis", pltscl.plot_rs_analysis_by_target
    )
    PlotRegistry.register(
        "hurst_variance_time",
        "Variance-Time Analysis",
        pltscl.plot_variance_time_analysis,
    )
    PlotRegistry.register(
        "hurst_peiorodogram",
        "Periodogram Analysis",
        pltscl.plot_periodogram_analysis,
    )
