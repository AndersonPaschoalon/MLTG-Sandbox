import argparse
import os
import sys

import commons.pylang.pylang as pl
from commons.config.experiment_config import ExperimentConfig
from commons.connectors.alchemy_connector import AlchemyConnector
from commons.formatter.datafile_name_formatter import DatafileNameFormatter
from trace_analyzer.analyzer.bandwidth import calc_bw_pps_fps
from trace_analyzer.loader.sniffer_wrapper import SnifferWrapper

VERSION = "v0.1"
PROGRAM_NAME = "trace_analyzer.py"
HELP_DESCRIPTION = """
Trace Analyzer - Traffic Generator Evaluation Tool

Purpose:
This tool provides scientific comparison of traffic generators against ground truth
data by automating metric extraction and visualization. It establishes a common
framework to objectively evaluate how closely different traffic generators replicate
real network traffic patterns across multiple dimensions.

Key Functionality:
1. Import experiment data into a structured database
2. Analyze raw traces to compute meaningful metrics
3. Generate publication-quality visualizations
4. Compare multiple traffic generators simultaneously

Typical Workflow:
1. Import experiment data (--load)
2. Analyze metrics (--analyze)
3. Generate visualizations (--plot or --plot-all)

Use Case Scenarios:

[Research Validation]
$ trace_analyzer.py --load campus_capture.xml campus_traffic
$ trace_analyzer.py --analyze campus_capture.xml campus_traffic
$ trace_analyzer.py --plot campus_capture.xml campus_traffic bw ground-truth,iperf,litgen
→ Validates which generator best matches real campus traffic bandwidth patterns

[Tool Comparison]
$ trace_analyzer.py --plot lab_test.xml tool_comparison pps ground-truth,scapy,tcpreplay
→ Compares packets-per-second accuracy across different generation tools

[Comprehensive Analysis]
$ trace_analyzer.py --plot-all enterprise_capture.xml enterprise_analysis
→ Generates all standard plots for complete enterprise traffic evaluation

Available Metrics:
• bw - Bandwidth distribution over time
• pps - Packet rate dynamics
• psd - Packet size distribution
• wavelet - Multiscale traffic patterns

Supported Tools:
• ground-truth - Original captured traffic
• iperf - Standard traffic generator
• litgen - Custom lightweight generator
• [Add your custom tools as needed]
"""


def _load_experiment_config(experiment_xml_file, experiment_name="*"):
    print(
        f"Importing experiment from: {experiment_xml_file} with name: {experiment_name}"
    )
    if not os.path.exists(experiment_xml_file):
        raise FileNotFoundError(f"{experiment_xml_file}")
    if experiment_name == "*":
        list_configs = ExperimentConfig.load(experiment_xml_file)
        return list_configs
    else:
        config = ExperimentConfig.get_by_name(experiment_xml_file, experiment_name)
        return config


def load_experiment(experiment_xml_file, experiment_name):
    config = _load_experiment_config(experiment_xml_file, experiment_name)
    print("#1 Loading data from Pcaps")
    pcap_fmt = DatafileNameFormatter(config.out_dir, config.name, "pcap")
    # list all *.pcap and client catpures. no tool_under_test means all will be returned.
    file_list = pcap_fmt.list_names("capture", "pcap", "client")
    sniffer = SnifferWrapper(config.experiment_dir(), config.name)
    # store ground truth
    sniffer.exec(config.pcap)
    for f in file_list:
        # store each experiment run
        # if i need recover this data later, I should use SnifferWrapper.trace_entry_name()
        sniffer.exec(f)


def list_experiments(experiment_xml_file):
    list_configs = _load_experiment_config(experiment_xml_file, "*")
    lout = []
    c: ExperimentConfig
    for c in list_configs:
        if not os.path.exists(c.experiment_db_dir()):
            print(f"Experiment {c.experiment_dir()} wasn't loaded yet.")
            continue
        sniffer = SnifferWrapper(c.experiment_dir(), c.name)
        l = sniffer.list_loaded_traces()
        lout.append(l)
    print("Loaded experiments.traces are:")
    for l in lout:
        for i in l:
            print(f"-\t{i}")


def analyze_experiment(experiment_xml_file, experiment_name):
    analisis_dir = "analisis"
    print(f"Analyzing experiment: {experiment_name} from file: {experiment_xml_file}")
    c = _load_experiment_config(experiment_xml_file, experiment_name)
    sniffer = SnifferWrapper(c.experiment_dir(), c.name)
    ltraces = sniffer.list_loaded_traces()
    for t in ltraces:
        print(f"Loading db connector for trace {t}")
        ac = sniffer.flowdb_connector(t)
        # Calculating bandwidth, packets per second and flows per second
        print(f"Calculating bandwidth, pps and fps {t}")
        df = calc_bw_pps_fps(ac)
        out_file = os.path.join(c.experiment_dir(), analisis_dir, f"bw_pps_fps.{t}.csv")
        pl.save_as_csv(df, out_file)


def plot_all(xml_file, experiment_name):
    print(
        f"Plotting all analyses for experiment: {experiment_name} from file: {xml_file}"
    )


def plot_custom(xml_file, experiment_name, plot_name, tool_list):
    print(
        f"Custom plot: {plot_name} for experiment: {experiment_name} from file: {xml_file}"
    )
    print(f"Tools to be used (csv): {tool_list}")


def _test():
    t01 = False
    t02 = False
    t03 = True
    if t01:
        load_experiment(
            xml_file="scripts/xml/sample_tests.xml", experiment_name="Banana"
        )
    if t02:
        list_experiments("scripts/xml/sample_tests.xml")
    if t03:
        # TODO: testar!!
        analyze_experiment(
            xml_file="scripts/xml/sample_tests.xml", experiment_name="Banana"
        )


def main():
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description=HELP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,  # Preserves formatting
        epilog="For detailed documentation, see https://example.com/trace_analyzer",
    )

    parser.add_argument(
        "--version", action="store_true", help="Show version information and exit."
    )
    parser.add_argument(
        "--load",
        nargs=2,
        metavar=("experiment_xml_file", "experiment_name"),
        help="Import experiment data into TraceDb.",
    )
    parser.add_argument(
        "--list",
        nargs=1,
        metavar=("experiment_xml_file"),
        help="List all exported experiments in specified on experiment_xml_file.",
    )
    parser.add_argument(
        "--analyze",
        nargs=2,
        metavar=("experiment_xml_file", "experiment_name"),
        help="Analyze the experiment and store raw data in CSV.",
    )
    parser.add_argument(
        "--plot-all",
        nargs=2,
        metavar=("experiment_xml_file", "experiment_name"),
        help="Generate all predefined plots for the experiment.",
    )
    parser.add_argument(
        "--plot",
        nargs=4,
        metavar=(
            "experiment_xml_file",
            "experiment_name",
            "plot_name",
            "csv_tool_list",
        ),
        help="Generate custom plot with specified tools.",
    )

    args = parser.parse_args()

    if args.version:
        print(f"{PROGRAM_NAME} {VERSION}")
        sys.exit(0)
    if args.load:
        load_experiment(*args.load)
    elif args.list:
        list_experiments(*args.list)
    elif args.analyze:
        analyze_experiment(*args.analyze)
    elif args.plot_all:
        plot_all(*args.plot_all)
    elif args.plot:
        plot_custom(*args.plot)


if __name__ == "__main__":
    # main()
    _test()
