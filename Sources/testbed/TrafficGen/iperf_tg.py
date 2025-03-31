import time
from testbed.TrafficGen.traffic_gen import TrafficGen
from Utils.PcapUtils import PcapUtils
from mininet.util import custom, waitListening, decode

class IperfGen(TrafficGen):

    def __init__(self, pcap, client, server, client_cfg, server_cfg, verbose, client_log, server_log):
        self.client_log = f"{client_log}.log"
        self.server_log = f"{server_log}.log"        
        self.iperf_client_cmd, self.estimate_exec_time = \
            IperfGen.iperf_cmd_client(pcap_file=self.pcap,
                                      dst_ipaddr=self.ip_server,
                                      src_ipaddr=self.ip_client,
                                      client_log_file=self.client_log)
        self.tg_name = "Iperf3"
        if self.verbose:
            print("[iperf] initialized")
        self.proc_server = None


    # Overwrite
    def name(self):
        return self.tg_name

    # Overwrite
    def server_listen(self):
        server_cmd = f"iperf3 -s "
        if self.verbose:
            print(f"[iperf:client] server IP address is {self.server.IP()}")
            print(f"[iperf:server] running command <{server_cmd}>")
        self.proc_server = self.server.popen(server_cmd)
        if self.verbose:
            print(f"[iperf:server] server process is running...")

    # Overwrite
    def server_stop(self):
        self.proc_server.terminate()
        if self.verbose:
            print(f"[iperf:server] server process is terminated")
        print(f'[iperf:server] stdout: {decode(self.proc_server.stdout.readline())}')

    # Overwrite
    def client_start(self):
        if ret < 0:
            return ret
        if self.verbose:
            print(f"[iperf:client] client IP address is {self.client.IP()}")
            print(f"[iperf:client] running command <{self.iperf_client_cmd}>")
        # waitListening(self.client, self.server, 5001)
        # time.sleep(2)
        self.proc_client = self.client.popen(self.iperf_client_cmd)
        return self.estimate_exec_time

    # Overwrite
    def client_stop(self):
        if self.verbose:
            print(f"terminating Iper3 instances on client.")
        self.proc_client.terminate()
        print(f'[iperf:client] stdout: {decode(self.proc_client .stdout.readline())}')

    @staticmethod
    def iperf_cmd_client(pcap_file, dst_ipaddr, src_ipaddr, client_log_file):
        tx_bytes, time_sec, n_packets_tcp, n_packets_udp, n_packets_other = \
            PcapUtils.pcap_summarizer(pcap_file)
        protocol = "" if (n_packets_tcp > n_packets_udp) else "-u"
        time_int = int(time_sec)
        tx_str = ""

        if tx_bytes <=0:
            return ""
        elif tx_bytes < 10**3:
            tx_str = f"{tx_bytes}"
        elif tx_bytes < 10**6:
            tx_kb = int(tx_bytes/(10**3))
            tx_str = f"{tx_kb}K"
        elif tx_bytes < 10**9:
            tx_mb = int(tx_bytes/(10**6))
            tx_str = f"{tx_mb}M"
        else: # tx_bytes > 10**9
            tx_gb = int(tx_bytes/(10**9))
            tx_str = f"{tx_gb}G"

        client_cmd = f"sudo iperf3 -c {dst_ipaddr} -B {src_ipaddr} {protocol} -b {tx_str} -t {time_int} "
        return client_cmd, time_int

