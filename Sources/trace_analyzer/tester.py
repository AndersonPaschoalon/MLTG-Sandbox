import traceback

import trace_analyzer.analysis_registry as analysis_registry
import trace_analyzer.analyzer as analyzer
import trace_analyzer.core as core
import trace_analyzer.data_loader as data_loader
import trace_analyzer.plotter as plotter


def run_tests():
    print("#########")
    target_list = []
    data_loader.load_stored_analysis_data(target_list=target_list)
    plotter.plot_violin_interarrival(target_list=target_list)
    plotter.plot_violin_pkt(target_list=target_list)
    plotter.plot_box_interarrival(target_list=target_list)
    plotter.plot_box_pkt(target_list=target_list)
    plotter.plot_interarrival_pdf(target_list=target_list)
    plotter.plot_interarrival_cdf(target_list=target_list)
    plotter.plot_interarrival_by_index(target_list=target_list)
    plotter.plot_bw_pps_fps_refactored("bandwidth", target_list=None)
    plotter.plot_bw_pps_fps_refactored("packet_per_second", target_list=None)
    plotter.plot_bw_pps_fps_refactored("flow_per_second", target_list=None)
    plotter.plot_pktsize_histogram(target_list=None)
    plotter.plot_bandwidth_cdf()
    plotter.plot_packet_load_cdf()
    plotter.plot_payload_size_cdf()
    plotter.plot_burst_size_violin()
    plotter.plot_inter_burst_interval_cdf()
    plotter.plot_burst_duration_violin()
    plotter.plot_wavelet_multiresolution_energy_analysis()


def test_main():
    try:
        # create_env("scripts/xml/sample_tests.xml", "Banana")
        # load_env()
        # print(mem)
        cmd_list_tr = False
        cmd_mk_env = False
        cmd_rm_env = False
        cmd_analyze = True
        cmd_run_tests = True

        # --list-traces
        if cmd_list_tr:
            analyzer.list_experiments()
        # --mk-env
        if cmd_mk_env:
            core.create_env("scripts/xml/sample_tests.xml", "Banana")
            analyzer.load_into_snifferdb()
            analyzer.list_experiments()
        # --rm-env
        if cmd_rm_env:
            core.rm_env()
        if cmd_analyze:
            analyzer.analyze_experiment_and_store()
        if cmd_run_tests:
            run_tests()
    except Exception as ex:
        print("********** EXCEPTION **********")
        traceback.print_exc()
        print("*******************************")
        print(ex)


if __name__ == "__main__":
    test_main()
