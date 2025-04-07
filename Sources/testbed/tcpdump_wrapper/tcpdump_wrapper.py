import threading

from mininet.node import Host
from mininet.util import custom, decode, waitListening

from testbed.utils.mininet_utils import MininetUtils


class TcpdumpWrapper:
    def __init__(self):
        self.lock = threading.Lock()
        self.running = False
        self.mn_host = None
        self.tcpdump = None
        self.log_file = None

    def start(
        self,
        mn_host: Host,
        interface_index: int = 0,  # Default to first interface
        pcap_file: str = "default",
        log_file: str = "",
    ) -> bool:
        """Start tcpdump on a host's interface.

        Args:
            mn_host: Mininet host object.
            interface_index: Index of the interface (default: 0).
            pcap_file: Output PCAP filename (without .pcap).
            log_file: If provided, saves tcpdump output to this file.

        Returns:
            bool: True if started successfully, False otherwise.
        """
        with self.lock:
            if self.running:
                print(f"[tcpdump] Already running on host {mn_host.name}")
                return False

            # Get interface name (e.g., h1-eth0) using MininetUtils
            interface_info = MininetUtils.get_host_interface(mn_host, interface_index)
            if not interface_info:
                print(f"[tcpdump] No interface found at index {interface_index}")
                return False

            interface = interface_info["interface"]
            self.mn_host = mn_host
            self.log_file = log_file

            # Build tcpdump command
            command = f"tcpdump -s 0 -i {interface} -U -w {pcap_file}.pcap"
            print(f"[tcpdump] Starting on {mn_host.name}: {command}")

            # Redirect output to log_file if provided
            if log_file:
                command += f" > {log_file}.log 2>&1"

            # Start tcpdump in the host's namespace
            self.tcpdump = mn_host.popen(command, shell=True)
            self.running = True
            return True

    def stop(self) -> bool:
        """Stop tcpdump and clean up."""
        with self.lock:
            if not self.running or not self.tcpdump:
                print("[tcpdump] Not running")
                return False

            print(f"[tcpdump] Stopping on host {self.mn_host.name}")
            self.tcpdump.terminate()
            self.running = False
            return True


"""
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
"""
