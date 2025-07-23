import trace_analyzer.metrics.burstiness as metrics_burstiness
import trace_analyzer.metrics.flow_level as metrics_flow_level
import trace_analyzer.metrics.packet_level as metrics_packet_level
import trace_analyzer.metrics.scaling as metrics_scaling
from trace_analyzer.registers.analysis_registry import AnalysisRegistry


def register_all_analysis():

    # Bandwidth/PPS/FPS analysis
    AnalysisRegistry.register(
        name="bw_pps_fps",
        display_name="Bandwidth/PPS/FPS",
        mem_attribute="bwdata_target",
        csv_prefix="bw_pps_fps",
        metric_fn=metrics_packet_level.calc_bw_pps_fps_as_df,
        requires_min_time=True,  # Needs time alignment
    )
    # Packet inter-arrival analysis
    AnalysisRegistry.register(
        name="interarrival",
        display_name="Packet Inter-arrival",
        mem_attribute="interdata_target",
        csv_prefix="inter_arrival_ttl",
        metric_fn=metrics_packet_level.get_packet_arrival_df,
        requires_min_time=True,
    )
    # Burst metrics (split into three separate registrations)
    AnalysisRegistry.register(
        name="burst_sizes",
        display_name="Burst Sizes",
        mem_attribute="burstsizesdata_target",
        csv_prefix="burst_sizes",
        metric_fn=metrics_burstiness.calc_burst_sizes_as_df,
        requires_min_time=False,
    )
    AnalysisRegistry.register(
        name="burst_durations",
        display_name="Burst Durations",
        mem_attribute="burstdurdata_target",
        csv_prefix="burst_durations",
        metric_fn=metrics_burstiness.calc_burst_durations_as_df,
        requires_min_time=False,
    )
    AnalysisRegistry.register(
        name="burst_intervals",
        display_name="Burst Intervals",
        mem_attribute="burstinterdata_target",
        csv_prefix="burst_intervals",
        metric_fn=metrics_burstiness.calc_burst_intervals_as_df,
        requires_min_time=False,
    )
    # Wavelet analysis
    AnalysisRegistry.register(
        name="wavelet",
        display_name="Wavelet Energy",
        mem_attribute="waveletdata_target",
        csv_prefix="wavelet",
        metric_fn=metrics_scaling.calc_wavelet_as_df,
        requires_min_time=False,
    )

    AnalysisRegistry.register(
        name="hurst_rs",
        display_name="Hurst R/S Analysis",
        mem_attribute="hurstrsdata_target",
        csv_prefix="hurst_rs",
        metric_fn=metrics_scaling.calc_rs_analysis_as_df_dense,
        requires_min_time=False,
    )

    AnalysisRegistry.register(
        name="hurst_variancetime",
        display_name="Hurst Variance-Time Analysis",
        mem_attribute="hurstvariancetimedata_target",
        csv_prefix="hurst_variancetime",
        metric_fn=metrics_scaling.calc_variance_time_analysis_as_df,
        requires_min_time=False,
    )

    AnalysisRegistry.register(
        name="hurst_periodogram",
        display_name="Hurst Periodogram Analysis",
        mem_attribute="hurstperiodogramdata_target",
        csv_prefix="hurst_periodogram",
        metric_fn=metrics_scaling.calc_periodogram_as_df,
        requires_min_time=False,
    )

    AnalysisRegistry.register(
        name="interarrival_correlogram",
        display_name="Interarrival Correlogram",
        mem_attribute="interarrivalcorrelogram_target",
        csv_prefix="interarrival_correlogram",
        metric_fn=metrics_scaling.calc_interarrival_correlogram,
        requires_min_time=False,
    )

    # AnalysisRegistry.register(
    #    name="peak_packet_load",
    #    display_name="Peak Packet Load (pkt/s) – CDF",
    #    mem_attribute="peak_packet_load_data_target",
    #    csv_prefix="peak_packet_load",
    #    metric_fn=metrics_packet_level.calc_peak_load_stats,
    #    requires_min_time=False,
    # )

    AnalysisRegistry.register(
        name="idc_per_timescale",
        display_name="Index of Dispersion for Counts (IDC)",
        mem_attribute="idc_per_timescale_data_target",
        csv_prefix="idc_per_timescale",
        metric_fn=metrics_scaling.calc_idc_per_timescale_as_df,
        requires_min_time=False,
    )
