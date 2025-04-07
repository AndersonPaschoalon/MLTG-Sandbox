import argparse
import logging
import os
import traceback

from testbed.logger.logger import Logger

Logger.initialize(
    "./logs/run_testbed.log", level_log=logging.DEBUG, level_console=logging.INFO
)

from testbed.experiment.experiment import Experiment


def print_version():
    print("Script Version: 1.0")
    return True


def run_experiments(experiment_list: str):
    logger = Logger.get()
    if experiment_list:
        if not os.path.exists(experiment_list):
            logger.error(f"Error: XML file '{experiment_list}' does not exist.")
            return False

    # parse the XML
    experiments = []
    try:
        experiments = Experiment.from_xml(experiment_list)
    except Exception as err:
        logger.error(Exception, err)
        logger.error("Stack Trace:")
        logger.error(traceback.format_exc())
        return False

    # run the experiments
    experiment: Experiment
    for experiment in experiments:
        # Execute the experiment as needed
        logger.info(f"Running Experiment: {experiment.config.name}")
        experiment.run()
    return True


def main():

    parser = argparse.ArgumentParser(description="Script to run a set of experiments.")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="store_true", help="Display script version and exit"
    )
    parser.add_argument(
        "--experiment-list",
        help="Specify the XML file containing experiment configurations",
    )

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
