import argparse
import os
import sys

import commons.pylang.pylang as pl
from commons.config.experiment_config import ExperimentConfig
from commons.connectors.alchemy_connector import AlchemyConnector
from commons.naming.analysis_data_name_formatter import AnalysisDataNameFormatter
from commons.naming.raw_data_name_formatter import RawDataNameFormatter
from trace_analyzer.analyzer.bandwidth import calc_bw_pps_fps
from trace_analyzer.loader.sniffer_wrapper import SnifferWrapper


def load_experiment(experiment_xml_file, experiment_name):
    config = _load_experiment_config(experiment_xml_file, experiment_name)
    print("#1 Loading data from Pcaps")
    pcap_fmt = RawDataNameFormatter(config.out_dir, config.name, "pcap")
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
    print(f"Analyzing experiment: {experiment_name} from file: {experiment_xml_file}")
    c = _load_experiment_config(experiment_xml_file, experiment_name)
    sniffer = SnifferWrapper(c.experiment_dir(), c.name)
    ltraces = sniffer.list_loaded_traces()
    fmt = AnalysisDataNameFormatter(c.out_dir, c.name)
    for t in ltraces:
        print(f"Loading db connector for trace {t}")
        ac = sniffer.flowdb_connector(t)
        # Calculating bandwidth, packets per second and flows per second
        print(f"Calculating bandwidth, pps and fps {t}")
        df = calc_bw_pps_fps(ac)
        pl.save_as_csv(df, fmt.mknameext("bw_pps_fps", t, "csv"))


def plot_all(xml_file, experiment_name):
    print(
        f"Plotting all analyses for experiment: {experiment_name} from file: {xml_file}"
    )


def plot_custom(xml_file, experiment_name, plot_name, tool_list):
    print(
        f"Custom plot: {plot_name} for experiment: {experiment_name} from file: {xml_file}"
    )
    print(f"Tools to be used (csv): {tool_list}")


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
