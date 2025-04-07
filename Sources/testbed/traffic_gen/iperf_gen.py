import time

from experiment.experiment_config import ExperimentConfig
from mininet.util import custom, decode, waitListening

from testbed.logger.logger import Logger
from testbed.traffic_gen.traffic_gen import TrafficGen
from testbed.utils.exceptions import InvalidPCAPError
from testbed.utils.pcap_utils import PcapUtils as putil


class IperfGen(TrafficGen):

    def __init__(self, client, server, config: ExperimentConfig):
        super().__init__(client, server, config)
        (
            self.tx_bytes,
            self.time_sec,
            self.n_pkt_tcp,
            self.n_pkt_udp,
            self.n_pkt_other,
        ) = putil.pcap_summarizer(self.pcap)
        self.proc_server = None
        self.proc_client = None
        self.cmd_server, self.cmd_client, self.wait_time = self._iperf_cmds()

    def server_listen(self):
        logger = Logger.get()
        logger.debug(f"[iperf:server] server IP address is {self.server.IP()}")
        logger.debug(f"[iperf:server] running command <{self.cmd_server}>")
        self.proc_server = self.server.popen(self.cmd_server)
        logger.info(f"[iperf:server] server process is running...")

    def server_stop(self):
        logger = Logger.get()
        self.proc_server.terminate()
        logger.info("[iperf:server] server process is terminated")
        logger.debug(
            f"[iperf:server] stdout: {decode(self.proc_server.stdout.readline())}"
        )

    def client_start(self):
        logger = Logger.get()
        logger.debug(f"[iperf:client] client IP address is {self.client.IP()}")
        logger.debug(f"[iperf:client] running command <{self.cmd_client}>")
        self.proc_client = self.client.popen(self.cmd_client)
        time.sleep(self.wait_time)

    def client_stop(self):
        logger = Logger.get()
        logger.debug(f"terminating Iper3 instances on client.")
        self.proc_client.terminate()
        logger.debug(
            f"[iperf:client] stdout: {decode(self.proc_client.stdout.readline())}"
        )

    def _iperf_cmds(self):
        cmd_server = f"iperf3 -s "
        protocol = "" if (self.n_pkt_tcp > self.n_pkt_udp) else "-u"
        time_int = int(self.time_sec)
        tx_str = ""

        if self.tx_bytes <= 0:
            raise InvalidPCAPError(
                self.pcap,
                details="tx_bytes <= 0. This is a invalid/unsupported pcap format or it is empty.",
            )
        elif self.tx_bytes < 10**3:
            tx_str = f"{self.tx_bytes}"
        elif self.tx_bytes < 10**6:
            tx_kb = int(self.tx_bytes / (10**3))
            tx_str = f"{tx_kb}K"
        elif self.tx_bytes < 10**9:
            tx_mb = int(self.tx_bytes / (10**6))
            tx_str = f"{tx_mb}M"
        else:  # tx_bytes > 10**9
            tx_gb = int(self.tx_bytes / (10**9))
            tx_str = f"{tx_gb}G"

        client_cmd = f"sudo iperf3 -c {self.ip_server} -B {self.ip_client} {protocol} -b {tx_str} -t {time_int} "
        return cmd_server, client_cmd, time_int
