import os

from commons.config.experiment_config import ExperimentConfig
from commons.enviroment.env import Env
from commons.enviroment.memory_store import MemoryStore
from trace_analyzer.core.sniffer_wrapper import SnifferWrapper
from trace_analyzer.core.state import (
    CMD_ANALYZE,
    CMD_MAKE_ENV,
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


"""
def _old_analyze_experiment_and_store():
    #
    # Analyze parsed experiment data and generate CSVs for plotting.
    #
    # Workflow:
    # 1. Load the experiment environment (`load_env()`).
    # 2. Abort if the experiment has already been analyzed (`env.ex_analyzed` flag).
    # 3. For each trace in `mem.traces_target`:
    #    - Open a DB connector (`mem.sniffer.flowdb_connector`).
    #    - Compute and export to CSV:
    #        a. Bandwidth, packets per second, and flows per second (`ADNF.BW_PPS_FPS`).
    #        b. Packet inter-arrival times (`ADNF.INTERARRIVAL`).
    #        c. Burst metrics:
    #            - Burst sizes (`ADNF.BURST_SIZES`),
    #            - Burst durations (`ADNF.BURST_DURATIONS`),
    #            - Inter-burst intervals (`ADNF.BURST_INTERVALS`).
    #
    # Notes:
    # - CSV files are named and stored via `mem.anf.mknameext`.
    # - Analysis will not proceed if already marked as analyzed.
    # - To redo the analysis:
    #  Use `{CMD_RM_ENV}` to remove the environment, `{CMD_MAKE_ENV}` to reload, and `{CMD_ANALYZE}` to analyze again.
    #
    # Returns:
    #    bool: False if analysis is skipped due to prior completion; True otherwise.
    # 

    def bw_pps_fps(target: str, ac: AlchemyConnector):
        df = metrics_estimator.calc_bw_pps_fps_as_df(ac)
        csv_file = mem.anf.mknameext(ADNF.BW_PPS_FPS, target, "csv")
        df.to_csv(csv_file, index=False)
        return csv_file

    def interarrival(target: str, ac: AlchemyConnector):
        df = metrics_estimator.get_packet_arrival_df(ac)
        csv_file = mem.anf.mknameext(ADNF.INTERARRIVAL, target, "csv")
        df.to_csv(csv_file, index=False)
        return csv_file

    def burst_metrics(target: str, ac: AlchemyConnector, inter_arrival_threshould=0.01):
        #
        #Analyze bursts for a given target and DB connector.
        #- Burst: sequence of packets where inter-arrival < threshold.
        #- Saves burst sizes, durations, and inter-burst intervals to CSVs.
        #
        burst_sizes, burst_durations, inter_burst_intervals = (
            metrics_estimator.calc_burst_metrics(ac)
        )
        # Save results to CSVs
        f1 = mem.anf.mknameext(ADNF.BURST_SIZES, target, "csv")
        pd.DataFrame({"burst_size": burst_sizes}).to_csv(f1, index=False)
        f2 = mem.anf.mknameext(ADNF.BURST_DURATIONS, target, "csv")
        pd.DataFrame({"burst_duration": burst_durations}).to_csv(f2, index=False)
        f3 = mem.anf.mknameext(ADNF.BURST_INTERVALS, target, "csv")
        pd.DataFrame({"burst_interval": inter_burst_intervals}).to_csv(f3, index=False)
        return f1, f2, f3

    def wavelet_analysis(target: str, ac: AlchemyConnector):
        df = metrics_estimator.calc_wavelet_as_df(ac)
        csv_file = mem.anf.mknameext(ADNF.WAVELET, target, "csv")
        df.to_csv(csv_file, index=False)
        return csv_file

    load_env()
    if env.ex_analyzed:
        print(
            f"Experiment {env.ex_name} already analyzed. "
            f"If you want to do it again, it use {CMD_RM_ENV} to remove enviroment and {CMD_MAKE_ENV} and {CMD_ANALYZE} "
            f"to load enviroment and perform analysis. "
        )
        return False

    for trace, target in mem.traces_target:
        print(f"Loading db connector for trace {trace}")
        ac: AlchemyConnector = mem.sniffer.flowdb_connector(trace)
        # Calculate and exporting bandwidth, packets per second and flows per second
        bw_pps_fps(target, ac)
        interarrival(target, ac)
        burst_metrics(target, ac)
        wavelet_analysis(target, ac)

    env.ex_analyzed = True
    env.save(env_file)
"""


def analyze_experiment_and_store():
    load_env()
    if env.ex_analyzed:
        print(f"Experiment {env.ex_name} already analyzed...")
        return False

    for trace, target in mem.traces_target:
        # load connector to the database
        ac = mem.sniffer.flowdb_connector(trace)

        for analysis_name, analysis_def in AnalysisRegistry.get_all().items():
            fn_name = analysis_def["metric_fn"].__name__
            print(f"Running {analysis_name} ({fn_name}) for {target}")
            df = analysis_def["metric_fn"](ac)
            csv_file = mem.anf.mknameext(analysis_def["csv_prefix"], target, "csv")
            df.to_csv(csv_file, index=False)

    env.ex_analyzed = True
    env.save(env_file)
