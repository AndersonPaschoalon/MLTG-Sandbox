import time
from TrafficGen.TrafficGen import TrafficGen
from Utils.PcapUtils import PcapUtils


class IperfGen(TrafficGen):

    def __init__(self, pcap, host_client, host_server, client_cfg, server_cfg, verbose):
        super().__init__(pcap, host_client, host_server, client_cfg, server_cfg, verbose)
        self.iperf_client_cmd, self.estimate_exec_time = \
            IperfGen.iperf_cmd_client(pcap_file=self.pcap,
                                      dst_ipaddr=self.ip_server,
                                      src_ipaddr=self.ip_client)
        self.iperf_server_cmd = IperfGen.iperf_cmd_server()
        self.iperf_kill_cmd = IperfGen.iperf_kill_cmd()
        self.tg_name = "Iperf3"
        self.server_proc = None
        if self.verbose:
            print("IperfGen initialized")

    # Overwrite
    def name(self):
        return self.tg_name

    # Overwrite
    def server_listen(self):
        super().server_listen()
        if self.verbose:
            print(f"{self.tg_name}.Server -> <{self.iperf_server_cmd}>")
        self.server_proc = self.host_server.popen(self.iperf_server_cmd)

    # Overwrite
    def server_stop(self):
        super().server_stop()
        self.server_proc.terminate()
        # result = self.host_client.cmd(self.iperf_kill_cmd)
        #print(f"[Server] Kill Iperf3 output:\n{result}")

    # Overwrite
    def client_start(self):
        ret = super().client_start()
        if ret < 0:
            return ret
        if self.verbose:
            print(f"{self.tg_name}.Client -> <{self.iperf_client_cmd}>")
            print(f"host_client.IP():{self.host_client.IP()}")
        self.host_client.sendCmd(self.iperf_client_cmd)
        return self.estimate_exec_time

    # Overwrite
    def client_stop(self):
        super().client_stop()
        if self.verbose:
            print(f"Killing Iper3 instances on client. Sending command <{self.iperf_kill_cmd}>")
        self.host_client.monitor()
        self.host_server.popen(self.iperf_kill_cmd)
        time.sleep(2)
        # print(f"[Client] Kill Iperf3 output:\n{result}")

    @staticmethod
    def iperf_cmd_server():
        return "iperf3 -s"

    @staticmethod
    def iperf_cmd_client(pcap_file, dst_ipaddr, src_ipaddr):
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

        client_cmd = f"iperf3 -c {dst_ipaddr} -B {src_ipaddr} {protocol} -b {tx_str} -t {time_int}"
        return client_cmd, time_int

    @staticmethod
    def iperf_kill_cmd():
        return "killall iperf3 -v"
