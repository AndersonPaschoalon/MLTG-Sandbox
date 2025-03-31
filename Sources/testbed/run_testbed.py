import argparse
import logging
import os
import sys
import traceback

from logger.logger import Logger

from testbed.Experiment.experiment import Experiment

Logger.initialize("./logs/run_testbed.log", level_log=logging.DEBUG, level_console=logging.INFO)


def print_version():
    print("Script Version: 1.0")
    return True


def run_experiments(experiment_list: str):
    if experiment_list:
        if not os.path.exists(args.experiment_list):
            print(f"Error: XML file '{experiment_list}' does not exist.")
            return False

    # parse the XML
    experiments = []
    try:
        experiments = Experiment.from_xml(experiment_list)
    except Exception as err:
        print(Exception, err)
        print("Stack Trace:")
        print(traceback.format_exc())
        return False

    # run the experiments
    experiment: Experiment
    for experiment in experiments:
        # Execute the experiment as needed
        print(f"Running Experiment: {experiment.name}")
        experiment.run()
    return True


def main():
    simitar_home = os.environ['SIMITAR_HOME']
    parser = argparse.ArgumentParser(description="Script to run a set of experiments.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true", help="Display script version and exit")
    parser.add_argument("--experiment-list", help="Specify the XML file containing experiment configurations")

    args = parser.parse_args()

    if args.version:
        print_version()
        return 0

    if args.experiment_list:
        ret = run_experiments(args.experiment_list)
        return 0 if ret else 1

    else:
        print("Invalid parameter. Use --help for usage information.")
        return 1


if __name__ == "__main__":
    main()
