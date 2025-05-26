import os

from commons.config.experiment_config import ExperimentConfig
from commons.enviroment.env import Env
from commons.enviroment.memory_store import MemoryStore
from commons.naming.analysis_data_name_formatter import (
    AnalysisDataNameFormatter as ADNF,
)
from commons.naming.plot_name_formatter import PlotNameFormatter as PNF
from commons.naming.raw_data_name_formatter import RawDataNameFormatter as RDNF
from trace_analyzer.snifferdb.sniffer_wrapper import SnifferWrapper

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
    def _load_target_data(file_type, mem_attr):
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
        data_types = [
            (ADNF.BW_PPS_FPS, "bwdata_target"),
            (ADNF.INTERARRIVAL, "interdata_target"),
            (ADNF.BURST_DURATIONS, "burstdurdata_target"),
            (ADNF.BURST_INTERVALS, "burstinterdata_target"),
            (ADNF.BURST_SIZES, "burstsizesdata_target"),
            (ADNF.WAVELET, "waveletdata_target"),
        ]
        for file_type, mem_attr in data_types:
            # sets a tuple (file, target) to the atribut xpto_target of the corresponding file prefix.
            _load_target_data(file_type, mem_attr)

    print("load_env done")
