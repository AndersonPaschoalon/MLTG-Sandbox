import time
from mininet.net import Mininet
from mininet.node import Host, Switch
from Utils.MininetUtils import MininetUtils
from Utils.OSUtils import OSUtils


class TrafficGen:

    def __init__(self, pcap, host_client, host_server, client_cfg, server_cfg, verbose):
        self.pcap = pcap
        self.client_cfg = client_cfg
        self.server_cfg = server_cfg
        self.server_running = False
        self.client_running = False
        self.client_if = client_cfg['if']
        self.server_if = server_cfg['if']
        self.client = host_client
        self.server = host_server
        self.verbose = verbose
        if self.verbose: print("TrafficGen.client_if:", self.client_if)
        if self.verbose: print("TrafficGen.server_if:", self.server_if)
        self.ip_client = self.client.IP()
        self.ip_server = self.server.IP()
        self.tg_name = "TrafficGen"
        if self.verbose: print("TrafficGen.ip_client:", self.ip_client)
        if self.verbose: print("TrafficGen.ip_server:", self.ip_server)
        # OSUtils.breakpoint("@ TrafficGen after initializing the constructor")

    #
    # METADATA
    #
    def name(self):
        return self.tg_name

    #
    # SERVER
    #

    def server_listen(self):
        if self.server_running:
            print(f"TrafficGen Server is already running...")
            return False
        self.server_running = True

    def server_stop(self):
        self.server_running = False

    #
    # CLIENT
    #

    def client_start(self):
        if self.client_running:
            print(f"TrafficGen Client is already in use of...")
            return False
        self.client_running = True
        return True

    def client_stop(self):
        self.client_running = False

