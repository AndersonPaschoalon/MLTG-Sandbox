import subprocess

import pandas as pd
from mininet.net import Mininet
from mininet.node import Host, Switch


class QoSMonitor:
    """
    Monitors network quality metrics during experiments by running background probes.
    Measures:
    - Jitter (via ping between non-interfering hosts)
    - Queue length (via tc on switches)

    Usage:
    1. Create instance with network reference
    2. Start probes before traffic generation
    3. Stop probes after traffic ends

    Example:
        qmon = QoSMonitor(net)
        ping_probe = qmon.start_ping_probe(h2, h4, "ping.csv")
        queue_mon = qmon.start_queue_monitor(s1, "queue.csv")
        # ... run traffic ...
        qmon.stop_all()
    """

    def __init__(self, net: Mininet):
        """
        Args:
            net: Mininet network object containing hosts/switches
        """
        self.net = net
        self.active_probes = []

    def start_ping_probe(
        self, src: Host, dst: Host, output_file: str
    ) -> subprocess.Popen:
        """
        Starts continuous ping between non-interfering hosts to measure jitter.

        Args:
            src: Source host (e.g., h2)
            dst: Destination host (e.g., h4)
            output_file: Path to save CSV results (timestamp,rtt_ms)

        Returns:
            Popen process handle (automatically tracked for cleanup)
        """
        cmd = (
            f"ping -i 0.1 {dst.IP()} | "
            f"awk -F'[ =]' '/time=/" + '{print systime()"_"$1,$8}\' > {output_file}'
        )
        proc = src.popen(cmd, shell=True)
        self.active_probes.append(proc)
        return proc

    def start_queue_monitor(self, switch: Switch, output_file: str) -> subprocess.Popen:
        """
        Monitors queue backlog on switch interface using tc.

        Args:
            switch: Switch to monitor (e.g., s1)
            output_file: Path to save CSV results (timestamp,backlog_packets)

        Returns:
            Popen process handle (automatically tracked for cleanup)
        """
        intf = switch.defaultIntf()
        cmd = (
            f"while true; do "
            + f"echo $(date +%s) $(tc -s qdisc show dev {intf} | "
            + f"grep -m1 backlog | awk '{{print $8}}') >> {output_file}; "
            + f"sleep 0.1; done"
        )
        proc = switch.popen(cmd, shell=True)
        self.active_probes.append(proc)
        return proc

    def stop_all(self):
        """Terminates all active measurement processes."""
        for proc in self.active_probes:
            proc.terminate()
        self.active_probes = []


class PingProbe:
    def __init__(self, process, results_file):
        self.process = process
        self.results_file = results_file

    @property
    def results(self):
        df = pd.read_csv(self.results_file, sep=" ", names=["time", "rtt"])
        df["jitter"] = df["rtt"].diff().abs()
        return df


class QueueMonitor:
    def __init__(self, process, results_file):
        self.process = process
        self.results_file = results_file

    @property
    def results(self):
        return pd.read_csv(self.results_file, sep=" ", names=["timestamp", "backlog"])
