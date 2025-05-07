import argparse
import sys

import trace_analyzer_functions as taf

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


def _test():
    t01 = False
    t02 = False
    t03 = True
    if t01:
        taf.load_experiment(
            experiment_xml_file="scripts/xml/sample_tests.xml", experiment_name="Banana"
        )
    if t02:
        taf.list_experiments("scripts/xml/sample_tests.xml")
    if t03:
        taf.analyze_experiment(
            experiment_xml_file="scripts/xml/sample_tests.xml", experiment_name="Banana"
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
        taf.load_experiment(*args.load)
    elif args.list:
        taf.list_experiments(*args.list)
    elif args.analyze:
        taf.analyze_experiment(*args.analyze)
    elif args.plot_all:
        taf.plot_all(*args.plot_all)
    elif args.plot:
        taf.plot_custom(*args.plot)


if __name__ == "__main__":
    # main()
    _test()
