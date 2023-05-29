from TrafficGen.TrafficGen import TrafficGen
from Utils.MininetUtils import MininetUtils
from TrafficGen.IperfWrapper import pcap_to_iperf_cmd, iperf_server_cmd, iperf_kill_cmd
from threading import Thread


class IperfGen(TrafficGen):

    def __init__(self, pcap, host_client, host_server, client_cfg, server_cfg, verbose):
        super().__init__(pcap, host_client, host_server, client_cfg, server_cfg, verbose)
        client_cmd, time_sec = pcap_to_iperf_cmd(self.pcap, self.ip_server, self.ip_client)
        self.estimate_exec_time = time_sec
        self.iperf_client_cmd = client_cmd
        self.iperf_server_cmd = iperf_server_cmd()
        self.iperf_kill_cmd = iperf_kill_cmd()
        self.tg_name = "Iperf"
        self.server_proc = None
        if self.verbose: print("IperfGen initialized")

    def name(self):
        return self.tg_name

    def server_listen(self):
        super().server_listen()
        if self.verbose: print(f"{self.tg_name}.Server -> <{self.iperf_server_cmd}>")
        self.server_proc = self.host_server.popen(self.iperf_server_cmd)
        # self.th_server = Thread(target=self.host_server.cmd(self.iperf_server_cmd))
        # # no need to care about the thread management
        # self.th_server.daemon = True
        # self.th_server.start()

    def server_stop(self):
        super().server_stop()
        self.server_proc.terminate()
        # self.host_server.sendInt(2)
        # if self.verbose: print(f"{self.tg_name}.Server -> <{self.iperf_kill_cmd}>")
        # self.host_server.cmd(self.iperf_kill_cmd)

    def client_start(self):
        ret = super().client_start()
        if ret < 0: return ret
        if self.verbose: print(f"{self.tg_name}.Client -> <{self.iperf_client_cmd}>")
        if self.verbose: print("self.host_client.shell", self.host_client.shell)
        if self.verbose: print("self.host_client.IP()", self.host_client.IP())
        self.host_client.sendCmd('ifconfig')
        out = self.host_client.waitOutput()
        print("waitOutput**", out)
        #self.host_client.startShell()
        #self.host_client.waiting = False
        self.host_client.sendCmd(self.iperf_client_cmd)
        # self.th_client.sendCmd(self.iperf_client_cmd)
        # self.th_client = Thread(target=self.host_client.cmd(self.iperf_client_cmd))
        return  self.estimate_exec_time


    def client_stop(self):
        super().client_stop()
        out = self.host_client.waitOutput()
        print("waitOutput**", out)
        # self.th_client.waitOutput()
        # self.th_client.join()

