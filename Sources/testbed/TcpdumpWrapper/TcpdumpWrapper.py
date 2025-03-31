import subprocess
import threading
import traceback
import time
from mininet.net import Mininet
from mininet.node import Host, Switch
from mininet.util import custom, waitListening, decode


class TcpdumpWrapper:

    def __init__(self, verbose=True):
        self.lock = threading.Lock()
        self.running = False
        self.mn_host = None
        self.tcpdump = None
        self.verbose = verbose

    def start(self, mn_host: Host, interface="eth0", pcap_file="default", log_file="tcpdump"):
        with self.lock:
            self.mn_host = mn_host
            if self.running:
                print("[tcpdump] tcpdump is already running.")
                return False
            if self.verbose:
                print("[tcpdump] Starting TcpdumpWrapper...")
            command = f"tcpdump -s 0 -i {interface} -U -w {pcap_file}.pcap --print "
            print(f"[tcpdump] executing command <{command}> on host {self.mn_host.IP()}")
            self.tcpdump = self.mn_host.popen(command)
            self.running = True
            return True

    def stop(self):
        if self.verbose:
            print(f"[tcpdump] Finalizing TCPDUMP process on host <{self.mn_host.IP()}>")
        self.tcpdump.terminate()
        self.running = False
        return True






