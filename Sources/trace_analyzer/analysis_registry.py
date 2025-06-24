import trace_analyzer.metrics_estimator as metrics_estimator
import trace_analyzer.plot_functions as plot_functions
from commons.naming.analysis_data_name_formatter import (
    AnalysisDataNameFormatter as ADNF,
)


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
        csv_prefix=ADNF.BW_PPS_FPS,
        metric_fn=metrics_estimator.calc_bw_pps_fps_as_df,
        requires_min_time=True,  # Needs time alignment
    )
    # Packet inter-arrival analysis
    AnalysisRegistry.register(
        name="interarrival",
        display_name="Packet Inter-arrival",
        mem_attribute="interdata_target",
        csv_prefix=ADNF.INTERARRIVAL,
        metric_fn=metrics_estimator.get_packet_arrival_df,
        requires_min_time=True,
    )
    # Burst metrics (split into three separate registrations)
    AnalysisRegistry.register(
        name="burst_sizes",
        display_name="Burst Sizes",
        mem_attribute="burstsizesdata_target",
        csv_prefix=ADNF.BURST_SIZES,
        metric_fn=metrics_estimator.calc_burst_sizes_as_df,
        requires_min_time=False,
    )
    AnalysisRegistry.register(
        name="burst_durations",
        display_name="Burst Durations",
        mem_attribute="burstdurdata_target",
        csv_prefix=ADNF.BURST_DURATIONS,
        metric_fn=metrics_estimator.calc_burst_durations_as_df,
        requires_min_time=False,
    )
    AnalysisRegistry.register(
        name="burst_intervals",
        display_name="Burst Intervals",
        mem_attribute="burstinterdata_target",
        csv_prefix=ADNF.BURST_INTERVALS,
        metric_fn=metrics_estimator.calc_burst_intervals_as_df,
        requires_min_time=False,
    )
    # Wavelet analysis
    AnalysisRegistry.register(
        name="wavelet",
        display_name="Wavelet Energy",
        mem_attribute="waveletdata_target",
        csv_prefix=ADNF.WAVELET,
        metric_fn=metrics_estimator.calc_wavelet_as_df,
        requires_min_time=False,
    )
