import csv
import os
import re
import threading
import time
from pathlib import Path

from mininet.node import Host


class PingMonitor:
    def __init__(
        self,
        client: Host,
        server: Host,
        log_file: str,
        ping_interval: float = 0.1,  # seconds between pings
        experiment_time: int = 60,  # total duration in seconds
    ):
        """
        Initialize Ping monitor between two hosts.

        Args:
            client: Host that will execute ping commands
            server: Host whose IP will be pinged (only used to get IP)
            log_file: logfile name (no extension)
            ping_interval: Time between ping packets (seconds)
            experiment_time: Total duration of ping test (seconds)
            count: Optional counter to avoid filename conflicts
        """
        self.lock = threading.Lock()
        self.running = False
        self.client = client
        self.server_ip = server.IP()  # Only need server's IP
        self.ping_interval = ping_interval
        self.experiment_time = experiment_time
        self.client_log = f"{log_file}.log"
        self.client_process = None

    def start(self) -> int:
        """Start ping process."""
        with self.lock:
            if self.running:
                print("[PingMonitor] Already running")
                return False

            # Calculate count based on duration and interval
            count = int(self.experiment_time / self.ping_interval)

            # Start ping process
            ping_cmd = (
                f"ping -i {self.ping_interval} "
                f"-c {count} "
                f"{self.server_ip} "
                f"> {self.client_log} 2>&1"
            )
            self.client_process = self.client.popen(ping_cmd, shell=True)

            self.running = True
        return self.experiment_time

    def stop(self):
        """Stop ping measurements."""
        with self.lock:
            if not self.running:
                print("[PingMonitor] Not running")
                return False
            self.running = False
        return True

    def _parse_ping_output_to_csv(self):
        """Parse ping output log file into CSV format."""
        if not os.path.exists(self.client_log):
            print(f"[PingMonitor] Log file not found: {self.client_log}")
            return

        # Create CSV filename by replacing .log with .csv
        csv_file = os.path.splitext(self.client_log)[0] + ".csv"

        ping_pattern = re.compile(
            r"(\d+) bytes from .*: icmp_seq=(\d+) ttl=(\d+) time=([\d.]+) ms"
        )

        with open(self.client_log, "r") as infile, open(
            csv_file, "w", newline=""
        ) as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["icmp_seq", "ttl", "rtt_ms"])  # Write header

            for line in infile:
                match = ping_pattern.search(line)
                if match:
                    # Extract and write the relevant data
                    writer.writerow(
                        [
                            int(match.group(2)),  # icmp_seq
                            int(match.group(3)),  # ttl
                            float(match.group(4)),  # time (rtt)
                        ]
                    )
