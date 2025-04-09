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
from testbed.net_tools.qos_monitor import QoSMonitor
from testbed.net_tools.tcpdump_wrapper import TcpdumpWrapper
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
        topo = SingleHopTopo()
        net = topo.initialize(cloud_loss=c.network_loss, cloud_delay=c.network_delay)
        h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
        s1, s2 = net.switches[0], net.switches[1]
        topo.simple_test()
        if c.display_mininet_cli:
            topo.cli()
        # define iperf traffic generator
        iperf = IperfGen(client=h1, server=h3, config=self.config)
        traffic_generators = [iperf]

        ex = []
        #
        # Trace Capture
        #
        logger.info("Pt 01 -- Synthetic trace capture")
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
                    pcap_file=vars["pcap"]["h1"],
                    log_file=vars["pcap"]["h3"],
                )
                logger.info(f"Starting capture on host3...")
                tcpdump_h3.start(
                    mn_host=h3,
                    interface_index=0,
                    pcap_file=vars["pcap"]["h1"],
                    log_file=vars["pcap"]["h3"],
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
                    "pcap.src": vars["pcap"]["h1"],
                    "pcap.src": vars["pcap"]["h3"],
                    "tg": tg.name(),
                }
                ex.append(ex_tg)

        #
        # QA/QoS Metrics
        #
        logger.info("Pt 03 -- QA/QoS metrics extraction")
        if c.run_capture:
            qmon = QoSMonitor(net)
            for tg in traffic_generators:
                # init vars
                vars = self._simple_topo_cap_vars(experiment_dir, tg)
                # Start measurements FIRST
                ping_proc = qmon.start_ping_probe(h2, h4, vars["qos"]["ping"])
                queue_proc = qmon.start_queue_monitor(s1, vars["qos"]["queue"])
                # Then run traffic
                logger.info(f"Starting {tg.name()} server...")
                tg.server_listen()
                logger.info(f"Starting {tg.name()} traffic generation...")
                tg.client_start()
                time.sleep(2)
                tg.client_stop()
                tg.server_stop()
                # Stop measurements LAST
                qmon.stop_all()
                ex.append(
                    {
                        "qos": {
                            "ping": vars["qos"]["ping"],
                            "queue": vars["qos"]["queue"],
                            "tg": tg.name(),
                        }
                    }
                )

        logger.info(f"Experiment {c.name} finalized successfully!")
        return ex

    def _simple_topo_cap_vars(self, experiment_dir, tg):
        # pcap - create output dir if does not exit
        pcap_dir = os.path.join(experiment_dir, "pcap")
        os.makedirs(pcap_dir, exist_ok=True)
        # build paths for pcaps
        cap_name_h1 = f"capture.host1.{self.count}.{tg.name()}"
        cap_name_h3 = f"capture.host3.{self.count}.{tg.name()}"
        cap_path_h1 = os.path.join(pcap_dir, cap_name_h1)
        cap_path_h3 = os.path.join(pcap_dir, cap_name_h3)
        # qos - create output dir if does not exit
        qos_dir = os.path.join(experiment_dir, "qos")
        os.makedirs(qos_dir, exist_ok=True)
        # build paths for qos
        file_ping = f"ping.{self.count}.{tg.name()}.csv"
        file_queue = f"queue.{self.count}.{tg.name()}.csv"
        path_ping = os.path.join(qos_dir, file_ping)
        path_queue = os.path.join(qos_dir, file_queue)
        vars = {
            "pcap": {
                "h1": cap_path_h1,
                "h3": cap_path_h3,
            },
            "qos": {
                "ping": path_ping,
                "queue": path_queue,
            },
        }
        return vars
