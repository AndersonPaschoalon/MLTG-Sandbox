import os.path
import time
import xml.etree.ElementTree as ET
from typing import List, Type

from mininet.cli import CLI
from mininet.link import OVSLink, TCLink
from mininet.net import Mininet
from mininet.node import Host, Switch

from commons.config.experiment_config import ExperimentConfig
from commons.exeptions.exceptions import PCAPNotFoundError
from commons.logger.logger import Logger
from commons.logger.logger_cron import LoggerCron
from commons.naming.raw_data_name_formatter import RawDataNameFormatter
from commons.pylang.os_utils import OSUtils as osutils
from testbed.net_tools.iperf3_monitor import Iperf3Monitor
from testbed.net_tools.ping_monitor import PingMonitor
from testbed.net_tools.tcpdump_wrapper import TcpdumpWrapper
from testbed.topos.single_hop_topo import SingleHopTopo
from testbed.traffic_gen.iperf_gen import IperfGen
from testbed.utils.mininet_utils import MininetUtils


class Experiment:

    def __init__(self, config: ExperimentConfig):
        """Initialize with a configuration object"""
        self.config: ExperimentConfig = config

    def __repr__(self) -> str:
        return f"Experiment(config={self.config})"

    @staticmethod
    def from_xml(file: str) -> List["Experiment"]:
        """
        Factory method to create experiments from XML
        """
        config_list = ExperimentConfig.load(file)
        return [Experiment(config) for config in config_list]

    def run(self):
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
        # backup existing directories
        osutils.ensure_clean_directory(os.path.join(c.out_dir, c.name))
        # Prepare eviroment
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

        #
        # Trace Capture
        #
        fmt_pcap = RawDataNameFormatter(c.out_dir, c.name, "pcap")
        logger.info("Pt 01 -- Synthetic trace capture")
        if c.run_capture:
            # Run capture tests
            tcpdump_h1 = TcpdumpWrapper()
            tcpdump_h3 = TcpdumpWrapper()
            for tg in traffic_generators:
                # init vars
                h1_cap = fmt_pcap.mkname("capture", tg.name(), "h1", "client")
                h3_cap = fmt_pcap.mkname("capture", tg.name(), "h3", "server")
                # start server
                logger.info(f"Starting {tg.name()} server...")
                tg.server_listen()
                # start capture
                logger.info(f"Starting capture on host1...")
                tcpdump_h1.start(
                    mn_host=h1,
                    interface_index=0,
                    out_file=h1_cap,
                )
                logger.info(f"Starting capture on host3...")
                tcpdump_h3.start(
                    mn_host=h3,
                    interface_index=0,
                    out_file=h3_cap,
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
                logger.debug(f"Experiment for tg:{tg.name()} DONE.")

        #
        # QA/QoS Metrics
        #
        logger.info("Pt 02 -- QA/QoS metrics RTT")
        fmt_qos = RawDataNameFormatter(c.out_dir, c.name, "qos")
        if c.run_qa:
            for tg in traffic_generators:
                ping_log = fmt_qos.mkname("ping", tg.name(), "h1", "client")
                ping = PingMonitor(h2, h4, ping_log)
                ping.start()
                # Then run traffic
                logger.info(f"Starting {tg.name()} server...")
                tg.server_listen()
                logger.info(f"Starting {tg.name()} traffic generation...")
                tg.client_start()
                time.sleep(2)
                tg.client_stop()
                tg.server_stop()
                # Stop measurements LAST
                ping.stop()
                ping._parse_ping_output_to_csv()

        logger.info("Pt 03 -- QA/QoS metrics JITTER/BW/LOSS")
        if c.run_qa:
            for tg in traffic_generators:
                log_client = fmt_qos.mkname("iperf3", tg.name(), "h2", "client")
                log_server = fmt_qos.mkname("iperf3", tg.name(), "h3", "server")
                perf = Iperf3Monitor(h2, h4, log_client, log_server)
                perf.start()
                # Then run traffic
                logger.info(f"Starting {tg.name()} server...")
                tg.server_listen()
                logger.info(f"Starting {tg.name()} traffic generation...")
                tg.client_start()
                time.sleep(2)
                tg.client_stop()
                tg.server_stop()
                # Stop measurements LAST
                perf.stop()

        logger.info(f"Experiment {c.name} finalized successfully!")
