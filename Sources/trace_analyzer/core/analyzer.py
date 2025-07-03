import os

from commons.config.experiment_config import ExperimentConfig
from commons.enviroment.env import Env
from commons.enviroment.memory_store import MemoryStore
from trace_analyzer.core.sniffer_wrapper import SnifferWrapper
from trace_analyzer.core.state import (
    CMD_RM_ENV,
    get_env,
    get_env_file,
    get_mem,
    load_env,
    rm_env,
)
from trace_analyzer.registers.analysis import AnalysisRegistry

env: Env = get_env()
mem: MemoryStore = get_mem()
env_file = get_env_file()


def list_experiments():
    """
    Lists all traces loaded into the sniffer database for each experiment defined in the XML file.

    This function:
    1. Loads all experiment configurations from the given XML file (supports multiple experiments).
    2. For each experiment, checks if its sniffer database has been initialized.
    3. If initialized, lists all traces that were previously loaded into the sniffer database.
    4. Prints a summary of all loaded traces.

    """
    load_env()
    lout = []
    c: ExperimentConfig
    for c in mem.list_configs:
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


def load_into_snifferdb():
    """
    Load packet capture data into the experiment sniffer database.

    Step-by-step:
    1. Load the environment configuration with `load_env()`.
    2. Abort if the experiment has already been loaded (based on `env.ex_loaded`).
    3. Call `mem.sniffer.exec()` on the ground-truth pcap.
    4. Iterate over client pcaps and parse them into the sniffer database.
    5. On error, delete the environment and raise the exception.
    6. Mark the experiment as loaded and save to disk.

    Returns:
        bool: True if load was performed; False if it was already loaded.
    """
    load_env()
    if env.ex_loaded:
        print(
            f"Experiment {env.ex_name} already loaded. If you want to reload it use {CMD_RM_ENV} before."
        )
        return False
    try:
        mem.sniffer.exec(mem.ground_truth)
        for pcap in mem.client_pcaps:
            mem.sniffer.exec(pcap)
    except Exception as ex:
        print(f"Error while trying to load experiment data: {ex}")
        rm_env()
        raise ex
    env.ex_loaded = True
    env.save(env_file)
    return True


def analyze_experiment_and_store():
    load_env()
    if env.ex_analyzed:
        print(f"Experiment {env.ex_name} already analyzed...")
        return False

    for trace, target, is_groundtruth in mem.traces_target:
        # load connector to the database
        ac = mem.sniffer.flowdb_connector(trace)

        for analysis_name, analysis_def in AnalysisRegistry.get_all().items():
            fn_name = analysis_def["metric_fn"].__name__
            display_name = analysis_def["display_name"]
            print("=" * 80)
            print(f"== Running <{display_name}>...")
            print(f"analysis_name:{analysis_name}, fn_name:{fn_name}, target:{target}")
            df = analysis_def["metric_fn"](ac)
            csv_file = mem.anf.mknameext(analysis_def["csv_prefix"], target, "csv")
            df.to_csv(csv_file, index=False)

    env.ex_analyzed = True
    env.save(env_file)
