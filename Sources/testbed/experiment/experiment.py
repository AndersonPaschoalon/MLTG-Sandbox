import os.path
import time
import xml.etree.ElementTree as ET
from typing import List, Type

from mininet.cli import CLI
from mininet.link import OVSLink, TCLink
from mininet.net import Mininet
from mininet.node import Host, Switch

from testbed.experiment.experiment_config import ExperimentConfig
from testbed.logger.logger import Logger
from testbed.logger.logger_cron import LoggerCron
from testbed.tcpdump_wrapper.tcpdump_wrapper import TcpdumpWrapper
from testbed.topos.single_hop_topo import SingleHopTopo
from testbed.traffic_gen.iperf_gen import IperfGen
from testbed.utils.exceptions import PCAPNotFoundError
from testbed.utils.mininet_utils import MininetUtils
from testbed.utils.os_utils import OSUtils


class Experiment:

    def __init__(self, config: ExperimentConfig):
        """Initialize with a configuration object"""
        self.config: ExperimentConfig = config
        self.count = 0

    def __repr__(self) -> str:
        return f"Experiment(config={self.config})"

    @staticmethod
    def from_xml(xml_file: str) -> List["Experiment"]:
        """
        Factory method to create experiments from XML
        """
        try:
            tree = ET.parse(xml_file)
            return [
                Experiment(ExperimentConfig.from_xml_element(elem))
                for elem in tree.findall("experiment")
            ]
        except Exception as e:
            raise ValueError(f"Error parsing XML: {e}") from e

    def run(self, count: int = 0):
        self.count = count
        logger = Logger.get()
        logger.debug(
            f"self.config.experiment_type:{self.config.experiment_type.lower()}"
        )
        if self.config.experiment_type.lower() == "simple-topo":
            return self._simple_topo()
        else:
            raise ValueError(
                f"Invalid experiment type {self.config.experiment_type.lower()}"
            )

    def _simple_topo(self):
        logger = Logger.get()
        c = self.config
        cron = LoggerCron(logger=logger, label=f"_simple_topo -> {c.name}")
        # Prepare eviroment
        experiment_dir = os.path.join(c.out_dir, c.name)
        OSUtils.create_directory(experiment_dir)
        if not os.path.exists(c.pcap):
            logger.error(f"Pcap file {c.pcap} does not exist!")
            raise PCAPNotFoundError(c.pcap)

        # create network
        sht = SingleHopTopo()
        net = sht.initialize(cloud_loss=c.network_loss, cloud_delay=c.network_delay)
        h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
        sht.simple_test()
        if c.display_mininet_cli:
            sht.cli()
        # define iperf traffic generator
        iperf = IperfGen(client=h1, server=h3, config=self.config)
        traffic_generators = [iperf]

        ex = []
        #
        # Trace Capture
        #
        if c.run_capture:
            # Run capture tests
            tcpdump_h1 = TcpdumpWrapper()
            tcpdump_h3 = TcpdumpWrapper()
            for tg in traffic_generators:
                # init vars
                vars = self._simple_topo_cap_vars(experiment_dir, tg)
                # start server
                logger.info(f"Starting {tg.name()} server...")
                tg.server_listen()
                # start capture
                logger.info(f"Starting capture on host1...")
                tcpdump_h1.start(
                    mn_host=h1,
                    interface_index=0,
                    pcap_file=vars["h1"]["pcap"],
                    log_file=vars["h1"]["log"],
                )
                logger.info(f"Starting capture on host3...")
                tcpdump_h3.start(
                    mn_host=h3,
                    interface_index=0,
                    pcap_file=vars["h3"]["pcap"],
                    log_file=vars["h3"]["log"],
                )
                # start traffic generation
                logger.info(f"Starting {tg.name()} traffic generation...")
                tg.client_start()
                # stop capture
                time.sleep(2)
                tg.client_stop()
                tcpdump_h1.stop()
                tcpdump_h3.stop()
                tg.server_stop()
                # record experiment info
                ex_tg = {
                    "pcap.src": vars["h1"]["pcap"],
                    "pcap.src": vars["h3"]["pcap"],
                    "tg": tg.name(),
                }
                ex.append(ex_tg)

        logger.info(f"Experiment {c.name} finalized successfully!")
        return ex

    def _simple_topo_cap_vars(self, experiment_dir, tg):
        pcap_dir = os.path.join(experiment_dir, "pcap")
        # create output dir if does not exit
        os.makedirs(pcap_dir, exist_ok=True)
        cap_name_h1 = f"capture.host1.{self.count}.{tg.name()}"
        cap_name_h3 = f"capture.host3.{self.count}.{tg.name()}"
        vars = {
            "h1": {"pcap": cap_name_h1, "log": cap_name_h1},
            "h3": {"pcap": cap_name_h3, "log": cap_name_h3},
        }
        return vars
