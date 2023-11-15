import xml.etree.ElementTree as ET
import os.path
import time
from mininet.net import Mininet
from mininet.node import Host, Switch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.link import OVSLink
from Topos.SingleHopTopo import SingleHopTopo
from Utils.MininetUtils import MininetUtils
from Utils.OSUtils import OSUtils
from TrafficGen.TrafficGen import TrafficGen
from TrafficGen.IperfGen import IperfGen
from TcpdumpWrapper.TcpdumpWrapper import TcpdumpWrapper
from NetQA.PingMeasurer import PingMeasurer


class Experiment:

    def __init__(self):
        self.name = ""
        self.pcap = ""
        self.out_dir = ""
        self.client_capture_if = ""
        self.server_capture_if = ""
        self.display_mininet_cli = False
        self.tcpdump_start_delay = 0
        self.tcpdump_stop_delay = 0
        self.verbose = False
        self.log_file = ""
        self.network_loss = 0.01
        self.network_delay = '20ms'
        self.run_capture = True
        self.run_jitter = True

    def run(self):
        """
        Execute the experiment loaded.
        :return:
        """
        # Prepare eviroment
        experiment_dir = os.path.join(self.out_dir, self.name)
        OSUtils.create_directory(experiment_dir)
        if not os.path.exists(experiment_dir):
            print(f"Pcap file {self.pcap} does not exist!")
            return False

        # create network
        net, topo = SingleHopTopo.initialize(cloud_loss=self.network_loss, cloud_delay=self.network_delay)
        h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
        h1_cfg = {
            "if": "h1-eth0",
        }
        h3_cfg = {
            "if": "h3-eth0",
        }
        if self.display_mininet_cli:
            CLI(net)

        # define iperf traffic generator
        client_log = os.path.join(experiment_dir, "iperf-client")
        server_log = os.path.join(experiment_dir, "iperf-server")
        iperf = IperfGen(pcap=self.pcap, client=h1, server=h3,
                        client_cfg=h1_cfg, server_cfg=h3_cfg, verbose=True, 
                        client_log=client_log, server_log=server_log)
        traffic_generators = [iperf]

        #
        # Trace Capture
        #
        if self.run_capture:
            # Run capture tests
            tcpdump = TcpdumpWrapper(verbose=True)
            for tg in traffic_generators:
                # init vars
                out_file = os.path.join(experiment_dir, f"capture.host1.{tg.name()}")
                tcpdump_log = os.path.join(experiment_dir, f"capture.host1.{tg.name()}")

                # start server
                print(f"Starting {tg.name()} server...")
                tg.server_listen()

                # start capture
                print(f"Starting capture on host1...")
                tcpdump.start(mn_host=h1, interface="h1-eth0", pcap_file=out_file, log_file=tcpdump_log)

                # start traffic generation
                print(f"Starting {tg.name()} traffic generation...")
                time_to_wait = tg.client_start()

                # wait to finish
                print(f"Waiting {time_to_wait}s")
                # time.sleep(time_to_wait)
                time.sleep(15) # for tests

                # stop capture
                time.sleep(2)
                tg.client_stop()
                tcpdump.stop()
                tg.server_stop()

        #
        # QA analysis
        #
        if self.run_jitter:
            # run network quality tests
            result_file = os.path.join(experiment_dir, "qa_result.txt")
            measurer = PingMeasurer(h4.IP(), self.qa_interval, self.qa_duration, result_file)
            for tg in traffic_generators:
                # start server
                print(f"Starting {tg.name()} server...")
                tg.server_listen()

                # start traffic generation
                print(f"Starting {tg.name()} traffic generation...")
                time_to_wait = tg.client_start()

                # start QA
                measurer.start(h3)

                # wait to finish
                print(f"Waiting {time_to_wait}s")

                # time.sleep(self.qa_duration)
                time.sleep(10) # for tests

                # stop capture
                tg.client_stop()
                time.sleep(2)
                tg.server_stop()
                

        SingleHopTopo.finalize(net)

        print(f"Experiment {self.name} finalized successfully!")
        return True

    @staticmethod
    def run_all(experiment_list):
        """
        Run a list of experiments.
        :param experiment_list:
        :return:
        """
        ex: Experiment
        for ex in experiment_list:
            ex.run()

    @staticmethod
    def from_xml(xml_file):
        """
        Create a list of experiment from a XML file. 
        :param xml_file: 
        :return: 
        """
        experiment_list = []
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for experiment_elem in root.findall("experiment"):
                experiment = Experiment()
                # Experiment Configuration
                experiment.name = experiment_elem.find("name").text
                experiment.pcap = experiment_elem.find("pcap").text
                experiment.out_dir = experiment_elem.find("out_dir").text
                experiment.display_mininet_cli = experiment_elem.find("display_mininet_cli").text.lower() == "true"
                experiment.verbose = experiment_elem.find("verbose").text.lower() == "true"
                experiment.log_file = experiment_elem.find("log_file").text
                # Network configuration
                experiment.tcpdump_start_delay = int(experiment_elem.find("tcpdump_start_delay").text)
                experiment.tcpdump_stop_delay = int(experiment_elem.find("tcpdump_stop_delay").text)
                experiment.client_capture_if = experiment_elem.find("client_capture_if").text
                experiment.server_capture_if = experiment_elem.find("server_capture_if").text
                experiment.network_loss = float(experiment_elem.find("network_loss").text)
                experiment.network_delay = experiment_elem.find("network_delay").text
                # Tests configuration
                experiment.run_capture = experiment_elem.find("run_capture").text.lower() == "true"
                experiment.run_jitter = experiment_elem.find("run_qa").text.lower() == "true"
                experiment.qa_duration = int(experiment_elem.find("qa_duration").text)
                experiment.qa_interval = int(experiment_elem.find("qa_interval").text)        

                experiment_list.append(experiment)

        except Exception as e:
            print(f"Error parsing XML: {e}")

        return experiment_list


if __name__ == '__main__':
    experiments_settings = Experiment.from_xml("sample.xml")
    for exp_sett in experiments_settings:
        print(f"Experiment Name: {exp_sett.name}")
        print(f"Verbose: {exp_sett.verbose}")

