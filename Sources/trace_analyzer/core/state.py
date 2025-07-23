import os

import commons.pylang.pylang as pl
import trace_analyzer.registers.analysis as analysis
from commons.config.experiment_config import ExperimentConfig
from commons.enviroment.env import Env
from commons.enviroment.memory_store import MemoryStore
from commons.logger.logger import Logger
from commons.naming.raw_data_name_formatter import RawDataNameFormatter as RDNF
from trace_analyzer.core.analysis_data_name_formatter import (
    AnalysisDataNameFormatter as ADNF,
)
from trace_analyzer.core.plot_name_formatter import PlotNameFormatter as PNF
from trace_analyzer.core.sniffer_wrapper import SnifferWrapper
from trace_analyzer.registers.analysis import AnalysisRegistry

env_file = ".trace_analyzer_env.json"
env = Env()
mem = MemoryStore()
CMD_RM_ENV = "--rm-env"
CMD_MAKE_ENV = "--mk-env"
CMD_ANALYZE = "--analyze"
CMD_LIST_TR = "--list-traces"


def get_env_file():
    return env_file


def get_env():
    return env


def get_mem():
    return mem


def set_env_param(param: str, new_value: object):
    print("Setting env.ex_analyzed as False")
    pl.set_json_param(env_file, "ex_analyzed", new_value)


def create_env(ex_xml, ex_name):
    print(f"Importing experiment from: {ex_xml} with name: {ex_name}")
    if os.path.exists(env_file):
        print(
            f"Enviroment for {ex_xml} alread created. Use {CMD_RM_ENV} to remove enviroment."
        )
        return
    config = ExperimentConfig.get_by_name(ex_xml, ex_name)
    env.ex_xml = ex_xml
    env.ex_name = ex_name
    env.ex_loaded = False
    env.ex_analyzed = False
    env.save(env_file)


def rm_env():
    if os.path.exists(env_file):
        print(f"rm {env_file}")
        os.remove(env_file)
        return
    print(f"Enviroment file {env_file} not found.")


def load_env():
    """
    Initialize and configure the experiment analysis environment by:
    1. Loading core configuration files
    2. Setting up directory structures and naming conventions
    3. Registering available data sources
    4. Loading previously generated analysis data

    The function follows a strict initialization sequence to ensure proper dependency
    ordering. All runtime objects are registered in the global `mem` object.

    Implementation Details:
    ----------------------
    1. ENVIRONMENT VALIDATION:
       - Verifies existence of environment file (env_file)
       - Loads experiment XML path and name from environment
       - Validates XML configuration file exists

    2. CORE CONFIGURATION LOADING:
       - Loads experiment configuration (ExperimentConfig)
       - Initializes naming formatters:
         * mem.rpcap: Raw PCAP file naming
         * mem.rcsv: Raw CSV file naming
         * mem.anf: Analysis file naming
         * mem.pnf: Plot file naming
       - Creates SnifferWrapper for trace access

    3. DATA SOURCE REGISTRATION:
       - Registers ground truth PCAP
       - Discovers and registers client/server PCAPs
       - If environment is marked as loaded (env.ex_loaded):
         a. Discovers all available traces via SnifferWrapper
         b. Parses trace metadata (target, ground truth status)
         c. Registers as (trace_path, target, is_ground_truth) tuples

    4. ANALYSIS DATA LOADING:
       - When env.ex_loaded=True:
         a. Initializes analysis registry
         b. For each registered analysis:
            i. Discovers CSV files using analysis-specific prefix
            ii. Extracts target information from filenames
            iii. Registers as (csv_path, target) tuples
         c. Handles both time-aligned and simple analyses

    Error Handling:
    --------------
    - Raises FileNotFoundError for missing critical files
    - Gracefully handles individual analysis load failures
    - Provides detailed console output about loading progress

    Side Effects:
    ------------
    - Populates global `mem` object with:
      * Configuration objects (mem.c, mem.list_configs)
      * Naming utilities (mem.rpcap, mem.anf, mem.pnf)
      * Data sources (mem.ground_truth, mem.client_pcaps, mem.server_pcaps)
      * Trace registry (mem.traces_target)
      * Analysis data maps (mem.*_df_map)
    - Modifies environment state (env.ex_loaded)
    - Creates directory structures if needed

    Returns:
    -------
    None

    Example Workflow:
    ----------------
    1. First call (fresh environment):
       - Only loads core configuration
       - Sets up directory structure
    2. Subsequent calls (env.ex_loaded=True):
       - Discovers all available data
       - Loads analysis CSVs for plotting
    """

    def _load_target_data(file_type, mem_attr):
        """
        Load analysis CSV files of a given type and register them as a list of (file, target) tuples in `mem`.

        This function:
        - Retrieves all CSV files associated with the specified `file_type` using `mem.anf.list_names()`.
        - Extracts the `test_target` from each file name using `mem.anf.parse()`.
        - Creates a list of tuples: (file_path, target_name).
        - Registers this list as an attribute of `mem` with name `mem_attr`.

        Parameters:
            file_type (str): The analysis file type (e.g., ADNF.WAVELET, ADNF.BURST_SIZES).
            mem_attr (str): The name of the attribute to set on `mem` to store the result.

        Side Effects:
            - Adds or overwrites `mem.<mem_attr>` with a list of tuples: [(file_path, target), ...].
            - Logs success or failure to the console.
        """
        try:
            data_target = []
            data_files = mem.anf.list_names(file_type, "csv")
            for file in data_files:
                target = mem.anf.parse(file, "test_target")
                data_target.append((file, target))
            setattr(mem, mem_attr, data_target)
            print(f"Loaded {len(data_target)} items for {mem_attr}")
        except Exception as e:
            print(f"Failed to load {mem_attr}: {e}")

    if not os.path.exists(env_file):
        raise FileNotFoundError(f"No experiment was loaded yet.")
    env.load(env_file)
    ex_xml = env.ex_xml
    ex_name = env.ex_name
    print(f"Importing experiment from: {ex_xml} with name: {ex_name}")
    if not os.path.exists(ex_xml):
        raise FileNotFoundError(f"{ex_xml}")
    config = ExperimentConfig.get_by_name(ex_xml, ex_name)
    list_configs = ExperimentConfig.load(env.ex_xml)

    # Register basic objects
    mem.list_configs = list_configs
    mem.c = config
    mem.rpcap = RDNF(config.out_dir, config.name, "pcap")
    mem.rcsv = RDNF(config.out_dir, config.name, "pcap")
    mem.anf = ADNF(config.out_dir, config.name)
    mem.pnf = PNF(config.out_dir, ex_name)
    mem.ex_name = config.name
    mem.ex_dir = config.experiment_dir()
    mem.sniffer = SnifferWrapper(config.experiment_dir(), config.name)
    mem.ground_truth = config.pcap
    mem.client_pcaps = mem.rpcap.list_names("capture", "pcap", "client")
    mem.server_pcaps = mem.rpcap.list_names("capture", "pcap", "server")

    # Register after --mk-env objects
    if env.ex_loaded:
        # register sniffer traces
        ltraces = mem.sniffer.list_loaded_traces()
        traces_target = []
        for trace in ltraces:
            target, is_groundthruth = mem.rpcap.parse(trace, RDNF.TEST_TARGET)
            tt = (trace, target, is_groundthruth)
            traces_target.append(tt)
        mem.traces_target = traces_target

        # # regiester csv data files
        analysis.register_all_analysis()
        for analysis_name, analysis_def in AnalysisRegistry.get_all().items():
            _load_target_data(analysis_def["csv_prefix"], analysis_def["mem_attribute"])

    print("load_env done")
