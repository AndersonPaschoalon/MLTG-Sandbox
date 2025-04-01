import os.path
import time
import xml.etree.ElementTree as ET
from typing import List, Type

from logger.logger import Logger
from logger.logger_cron import LoggerCron
from mininet.cli import CLI
from mininet.link import OVSLink, TCLink
from mininet.net import Mininet
from mininet.node import Host, Switch
from TcpdumpWrapper.TcpdumpWrapper import TcpdumpWrapper
from Topos.SingleHopTopo import SingleHopTopo
from Utils.MininetUtils import MininetUtils
from Utils.OSUtils import OSUtils

from testbed.Experiment.experiment_config import ExperimentConfig
from testbed.TrafficGen.iperf_tg import IperfGen
from testbed.TrafficGen.traffic_gen import TrafficGen


class Experiment:

    def __init__(self, config: ExperimentConfig):
        """Initialize with a configuration object"""
        self.config: ExperimentConfig = config

    def __repr__(self) -> str:
        return (f"Experiment(config={self.config})")

    @staticmethod
    def from_xml(xml_file: str) -> List['Experiment']:
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

    def run(self):
        logger = Logger.get()
        logger.debug(f"self.config.experiment_type:{self.config.experiment_type.lower()}")
        if self.config.experiment_type.lower() == "simple-topo":
            return self._simple_topo()
        else:
            raise ValueError(f"Invalid experiment type {self.config.experiment_type.lower()}")

    def _simple_topo(self):
        logger = Logger.get()
        c = self.config
        cron = LoggerCron(logger=logger, label=f"_simple_topo -> {c.name}")
        # Prepare eviroment
        experiment_dir = os.path.join(c.out_dir, c.name)
        OSUtils.create_directory(experiment_dir)
        if not os.path.exists(experiment_dir):
            logger.error(f"Pcap file {c.pcap} does not exist!")
            return False

        # create network
        net, topo = SingleHopTopo.initialize(cloud_loss=c.network_loss, cloud_delay=c.network_delay)
        h1, h2, h3, h4 =  net.hosts[0],  net.hosts[1],  net.hosts[2],  net.hosts[3]
        if c.display_mininet_cli:
            CLI(net)

        # define iperf traffic generator
        iperf = IperfGen(pcap=c.pcap, 
                         client=h1, 
                         server=h3,
                         client_cfg={"if": "h1-eth0"}, 
                         server_cfg={"if": "h3-eth0"}, 
                         verbose=True, 
                         client_log=os.path.join(experiment_dir, "iperf-client"), 
                         server_log=os.path.join(experiment_dir, "iperf-server"))
        traffic_generators = [iperf]

        #
        # Trace Capture
        #
        if c.run_capture:
            # Run capture tests
            tcpdump = TcpdumpWrapper(verbose=True)
            for tg in traffic_generators:
                # init vars
                out_file = os.path.join(experiment_dir, f"capture.host1.{tg.name()}")
                tcpdump_log = os.path.join(experiment_dir, f"capture.host1.{tg.name()}")

                # start server
                logger.info(f"Starting {tg.name()} server...")
                tg.server_listen()

                # start capture
                logger.info(f"Starting capture on host1...")
                tcpdump.start(mn_host=h1, interface="h1-eth0", pcap_file=out_file, log_file=tcpdump_log)

                # start traffic generation
                logger.info(f"Starting {tg.name()} traffic generation...")
                time_to_wait = tg.client_start()

                # wait to finish
                logger.info(f"Waiting {time_to_wait}s")
                # time.sleep(time_to_wait)
                time.sleep(15) # for tests

                # stop capture
                time.sleep(2)
                tg.client_stop()
                tcpdump.stop()
                tg.server_stop()

        SingleHopTopo.finalize(net)

        logger.info(f"Experiment {c.name} finalized successfully!")
        return True

