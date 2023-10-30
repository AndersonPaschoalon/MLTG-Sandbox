import subprocess
import threading
import traceback
import time
from mininet.net import Mininet
from mininet.node import Host, Switch


class TcpdumpWrapper:

    def __init__(self, verbose=True):
        self.running = False
        self.mn_host = None
        self.p_tcpdump = None
        self.verbose = verbose

    def start(self, mn_host: Host, interface="eth0", file="default"):
        if self.running:
            print("tcpdump is already running.")
            return False
        if self.verbose: print("Starting TcpdumpWrapper...")
        command = f"tcpdump -i {interface} -w {file}.pcap"
        print(f"TCPDUMP -> <{command}>")
        self.mn_host = mn_host
        # self.mn_host.startShell()
        print(self.mn_host.cmd("ifconfig"))
        self.p_tcpdump = self.mn_host.popen(command)
        self.running = True
        return True

    def stop(self):
        self.running = False
        self.p_tcpdump.terminate()
        return True






