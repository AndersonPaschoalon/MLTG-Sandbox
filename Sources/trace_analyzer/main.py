import argparse
import os
import sys

from commons.config.experiment_config import ExperimentConfig
from commons.formatter.datafile_name_formatter import DatafileNameFormatter
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


def load_experiment(experiment_xml_file, experiment_name):
    print(
        f"Importing experiment from: {experiment_xml_file} with name: {experiment_name}"
    )
    if not os.path.exists(experiment_xml_file):
        raise FileNotFoundError(f"{experiment_xml_file}")
    config = ExperimentConfig.get_by_name(experiment_xml_file, experiment_name)
    print("#1 Loading data from Pcaps")
    pcap_fmt = DatafileNameFormatter(config.out_dir, config.name, "pcap")
    # list all *.pcap and client catpures. no tool_under_test means all will be returned.
    ex_out_dir = os.path.join(config.out_dir, config.name)
    file_list = pcap_fmt.list_names("capture", "pcap", "client")
    sniffer = SnifferWrapper(ex_out_dir, config.name)
    # store ground truth
    sniffer.exec(config.pcap)
    for f in file_list:
        # store each experiment run
        # if i need recover this data later, I should use SnifferWrapper.trace_entry_name()
        sniffer.exec(f)


def list_experiments(experiment_xml_file):
    if not os.path.exists(experiment_xml_file):
        raise FileNotFoundError(f"{experiment_xml_file}")
    list_configs = ExperimentConfig.load(experiment_xml_file)
    lout = []
    for c in list_configs:
        ex_dirs = os.path.join(c.out_dir, c.name)
        db_dir = os.path.join(ex_dirs, "db")
        if not os.path.exists(db_dir):
            print(f"Experiment {ex_dirs} wasn't loaded yet.")
            continue
        sniffer = SnifferWrapper(ex_dirs, c.name)
        d = sniffer.list_experiments()
        lout.append(d)
    print(lout)


def analyze_experiment(experiment_xml_file, experiment_name):
    print(f"Analyzing experiment: {experiment_name} from file: {experiment_xml_file}")


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
    t02 = True
    if t01:
        load_experiment(
            xml_file="scripts/xml/sample_tests.xml", experiment_name="Banana"
        )
    if t02:
        list_experiments("scripts/xml/sample_tests.xml")


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

"""
Now i need your help on building the command line options for the trace analyzer component. (trace_analyzer.py)

# 1 Guidelines

First of all, you should not care about implementing business logic. Just follow the steps:
1. Add a command line option in the python .
2. The for specified option, capture the parameter provided in variables
3. pass the variables into function that implement the given operation.
4. in the implementation just print the values of the passed variables, except on --version and --help. 
5. -- version print the current version "v0.1" and the program name (as usually displaye in --version options)
6. --help prints a help manual of the trace_analyzer.py application.

# 2 Operations to implement

 (1) --import <experiment_xml_file> <experiment_name>: this  operation is responsible for importing the data from an already executed experiment, and store this information into a sqlite2 database (TraceDb) to be used later
 (2) --list: list all the exported experiments from TraceDb 
 (3) --analyze <experiment_xml_file> <experiment_name>: proceed with the analysis from --import, and calc and store all raw data to be ploted later in csv format. 
 (4) --plot-all <experiment_xml_file> <experiment_name>: plot all pre-defined available analysis and plots. 
 (5) --plot <experiment_xml_file> <experiment_name> <plot-name> <csv-tool-list>
 this command uses extracted data from --analyze implement custom plots for the provided experiment name. You should pass a the name of the plot to be implemented, and the list of tools (in csv format) to be compared. 
 Available plots are:
 1. bw - bandwidth
 2. pps - packet per seconds
 3. psd - packet size distrubution
 4. wavelet - wavelet multiresolution energy analysis
 Available toos are:
 1. ground-truth - use groud truth to plot original trace data
 2. iperf 
 3. litgen
 
# 3 About trace_analyzer.py

The purpose of trace analyzer is to provide a simple layer where we can automate the extraction of meaninfull data from raw data (pcaps, logs) collected from experiments wich were runned into the testbed component, so we can compare metrics and performance of many traffic generators against the ground truth, based on the most meaninfull metrics fround in the literature. In other words, we can stablish a common ground to tell wich traffic generator crafted the most realistic traffic comparaed to the ground-truth acording each one of the metrics. 



"""
