import trace_analyzer.metrics.burstiness as metrics_burstiness
import trace_analyzer.metrics.flow_level as metrics_flow_level
import trace_analyzer.metrics.packet_level as metrics_packet_level
import trace_analyzer.metrics.scaling as metrics_scaling


class AnalysisRegistry:
    _analyses = {}

    @classmethod
    def register(
        cls,
        name,
        display_name,
        mem_attribute,
        csv_prefix,
        metric_fn,
        requires_min_time=False,
    ):
        cls._analyses[name] = {
            "display_name": display_name,
            "mem_attribute": mem_attribute,
            "csv_prefix": csv_prefix,
            "metric_fn": metric_fn,
            "requires_min_time": requires_min_time,
        }

    @classmethod
    def get_all(cls):
        if len(cls._analyses) == 0:
            raise RuntimeError(
                "Error, you must load analysis registers before proceed. Call register_all_analysis() to do that."
            )
        return cls._analyses


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
