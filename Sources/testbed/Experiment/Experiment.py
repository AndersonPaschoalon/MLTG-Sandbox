import os
import logging
from TrafficGen import TrafficGen
from TcpdumpWrapper import TcpdumpWrapper


class Experiment:

    def __int__(self,
                src_pcap,
                capture_tool: TcpdumpWrapper,
                topology,
                tg: TrafficGen,
                logger: logging,
                experiment_duration = 10,
                capture_ether="eth0",
                experiment_name="Test",
                output_dir=""):
        self.src_pcap = src_pcap
        self.output_dir = output_dir
        self.capture_ether = capture_ether
        self.experiment_name = experiment_name
        self.out_pcap = ""
        self.experiment_duration = experiment_duration
        self.capture = capture_tool
        self.tg = tg
        self.out_pcap = os.path.join(self.output_dir, f"{tg.name()}_{self.experiment_name}.pcap")
        self.topology = topology
        self.logger = logging


    def run(self):

        self.logger.debug("Initializing topology")
        net, topo = self.topology.initialize()

        self.logger.debug("Testing topology topology")
        ret = self.topology.simple_test()
        if not ret:
            self.logger.error("Error testing topology")


        self.capture.start()
        self.tg.start()

        total_time = self.experiment_duration + self.capture.start_delay

        self.tg.finalize()
        self.capture.stop()
        self.topology.finalize()



