import argparse
import os
import sys
from Experiment import ExperimentSettings


def main():
    parser = argparse.ArgumentParser(description="Script to run a set of experiments.")
    parser.add_argument("--version", action="store_true", help="Display script version and exit")
    parser.add_argument("--help", action="store_true", help="Display help text and exit")
    parser.add_argument("--experiment-list", help="Specify the XML file containing experiment configurations")

    args = parser.parse_args()

    if args.version:
        print("Script Version: 1.0")
        sys.exit(0)

    if args.help:
        parser.print_help()
        sys.exit(0)

    if args.experiment_list:
        if not os.path.exists(args.experiment_list):
            print(f"Error: XML file '{args.experiment_list}' does not exist.")
            sys.exit(1)

        experiments = ExperimentSettings.from_xml(args.experiment_list)
        for experiment in experiments:
            # Execute the experiment as needed
            print(f"Running Experiment: {experiment.name}")

    else:
        print("Invalid parameter. Use --help for usage information.")
        sys.exit(1)

if __name__ == "__main__":
    main()
