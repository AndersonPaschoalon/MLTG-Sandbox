import argparse
import os
import sys
import traceback
import sys
from Experiment.Experiment import Experiment


def main():
    parser = argparse.ArgumentParser(description="Script to run a set of experiments.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true", help="Display script version and exit")
    parser.add_argument("--experiment-list", help="Specify the XML file containing experiment configurations")

    args = parser.parse_args()

    if args.version:
        print("Script Version: 1.0")
        return 0

    if args.experiment_list:
        if not os.path.exists(args.experiment_list):
            print(f"Error: XML file '{args.experiment_list}' does not exist.")
            return 1

        # parse the XML
        experiments = []
        try:
            experiments = Experiment.from_xml(args.experiment_list)
        except Exception as err:
            print(Exception, err)
            print("Stack Trace:")
            print(traceback.format_exc())
            return 1

        # run the experiments
        for experiment in experiments:
            # Execute the experiment as needed
            print(f"Running Experiment: {experiment.name}")
            experiment.run()

    else:
        print("Invalid parameter. Use --help for usage information.")
        return 1


if __name__ == "__main__":
    main()
