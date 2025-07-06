import trace_analyzer.core.data_loader as data_loader
import trace_analyzer.registers.plots as plots_register
from trace_analyzer.core.report_gen import ReportGen
from trace_analyzer.registers.plot_registry import PlotRegistry


def run_registered_plots(target_list=None, plot_names=None):

    data_loader.load_stored_analysis_data(target_list=target_list)
    plots_register.register_all_plotters()

    all_registered = PlotRegistry.get_all()
    to_run = plot_names or list(all_registered.keys())
    gen_report = (not target_list) and (not plot_names)

    all_plots = []
    for name in to_run:
        if name not in all_registered:
            print(f"[WARN] Plot '{name}' is not registered. Skipping.")
            continue
        print(f"[PLOT] Running plot: {name}")
        plot_file = PlotRegistry.call(name, target_list=target_list)
        if plot_file:
            all_plots.append(plot_file)

    if gen_report:
        rep = ReportGen(plot_lists=all_plots)
        rep.generate_report_html()
