import subprocess
import threading
import traceback
import time
from mininet.net import Mininet
from mininet.node import Host, Switch
from mininet.util import custom, waitListening, decode


class TcpdumpWrapper:

    def __init__(self, verbose=True):
        self.running = False
        self.mn_host = None
        self.tcpdump = None
        self.verbose = verbose

    def start(self, mn_host: Host, interface="eth0", file="default"):
        self.mn_host = mn_host
        if self.running:
            print("[tcpdump] tcpdump is already running.")
            return False
        if self.verbose:
            print("[tcpdump] Starting TcpdumpWrapper...")
        command = f"tcpdump -i {interface} -w {file}.pcap"
        print(f"[tcpdump] executing command <{command}> on host {self.mn_host.IP()}")
        self.tcpdump = self.mn_host.popen(command)
        self.running = True
        return True

    def stop(self):
        # self.mn_host.cmd("killall tcpdump -v")
        if self.verbose:
            print(f"[tcpdump] Finalizing TCPDUMP process on host <self.mn_host.IP()>")
        self.tcpdump.terminate()
        print(f'[tcpdump] stdout: {decode(self.tcpdump .stdout.readline())}')
        self.running = False
        return True






