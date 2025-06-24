import os

from commons.config.experiment_config import ExperimentConfig
from commons.enviroment.env import Env
from commons.enviroment.memory_store import MemoryStore
from commons.naming.analysis_data_name_formatter import (
    AnalysisDataNameFormatter as ADNF,
)
from commons.naming.plot_name_formatter import PlotNameFormatter as PNF
from commons.naming.raw_data_name_formatter import RawDataNameFormatter as RDNF
from trace_analyzer.sniffer_wrapper import SnifferWrapper

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
    Load experiment environment configuration and register key runtime objects into `mem`.

    This function performs the following steps:

    1. **Load environment configuration**:
        - Reads from `env_file` JSON and retrieves experiment XML and name.

    2. **Verify experiment configuration file exists**:
        - Raises FileNotFoundError if XML file is missing.

    3. **Register base runtime objects in `mem`**:
        - Experiment configuration (`mem.c`).
        - Raw data name formatter (`mem.rpcap` and `mem.rcsv`).
        - Analysis data name formatter (`mem.anf`).
        - Plot name formatter (`mem.pnf`).
        - Sniffer wrapper (`mem.sniffer`).
        - PCAP files for ground truth, client, and server.

    4. **If the experiment is marked as loaded**:
        - Register loaded sniffer traces (`mem.traces_target`) as list of (trace_file, target).
        - For each analysis type (e.g., wavelet, burst sizes):
            - Load associated CSVs.
            - Register as list of (file, target) tuples in corresponding `mem` attribute using `_load_target_data()`.

    Finalizes by printing `"load_env done"`.

    Raises:
        FileNotFoundError: If environment or experiment XML is missing.

    Side Effects:
        - Populates `mem` with all necessary runtime objects for analysis and plotting.
        - Prints progress to console.
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
            target = mem.rpcap.parse(trace, RDNF.TEST_TARGET)
            tt = (trace, target)
            traces_target.append(tt)
        mem.traces_target = traces_target

        # regiester csv data files
        data_types = [
            (ADNF.BW_PPS_FPS, "bwdata_target"),
            (ADNF.INTERARRIVAL, "interdata_target"),
            (ADNF.BURST_DURATIONS, "burstdurdata_target"),
            (ADNF.BURST_INTERVALS, "burstinterdata_target"),
            (ADNF.BURST_SIZES, "burstsizesdata_target"),
            (ADNF.WAVELET, "waveletdata_target"),
        ]
        for file_type, mem_attr in data_types:
            # sets a tuple (file, target) to the atribute xpto_target of the corresponding file prefix.
            _load_target_data(file_type, mem_attr)

    print("load_env done")
