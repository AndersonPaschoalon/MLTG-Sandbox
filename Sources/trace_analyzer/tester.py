import traceback

import trace_analyzer.core.analyzer as analyzer
import trace_analyzer.core.data_loader as data_loader
import trace_analyzer.core.plot_runner as plot_runner
import trace_analyzer.core.state as core_state
import trace_analyzer.plotter.plotters.burstiness as pltbrt
import trace_analyzer.plotter.plotters.packet_level as pltpkt
import trace_analyzer.plotter.plotters.scaling as pltscl


def run_all_plots():
    print("#########")
    target_list = []
    plot_names = []
    plot_runner.run_registered_plots(target_list=target_list, plot_names=plot_names)


def run_plot():
    print("#########")
    target_list = []
    plot_names = ["hurst_variance_time"]
    plot_runner.run_registered_plots(target_list=target_list, plot_names=plot_names)


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
            core_state.create_env("scripts/xml/sample_tests.xml", "Banana")
            analyzer.load_into_snifferdb()
            analyzer.list_experiments()
        # --rm-env
        if cmd_rm_env:
            core_state.rm_env()
        if cmd_analyze:
            analyzer.analyze_experiment_and_store()
        if cmd_run_tests:
            run_all_plots()
            # run_plot()
    except Exception as ex:
        print("********** EXCEPTION **********")
        traceback.print_exc()
        print("*******************************")
        print(ex)


if __name__ == "__main__":
    test_main()
