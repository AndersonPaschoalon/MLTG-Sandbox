import csv
import json
import os
import re
import threading
import time
from pathlib import Path

from mininet.node import Host


class Iperf3Monitor:
    def __init__(
        self,
        client: Host,
        server: Host,
        file_out_dir: str,
        file_base_name: str,
        bandwidth: str = "10M",
        time_to_report: int = 1,
        experiment_time: int = 60,
        count: int = 0,
        udp: bool = True,
    ):
        """
        Initialize iPerf3 monitor between two hosts.

        Args:
            udp: If True, uses UDP (-u flag), otherwise uses TCP
        """
        self.lock = threading.Lock()
        self.running = False
        self.client = client
        self.server = server
        self.bandwidth = bandwidth
        self.time_to_report = time_to_report
        self.experiment_time = experiment_time
        self.udp = udp

        # Ensure output directory exists
        Path(file_out_dir).mkdir(parents=True, exist_ok=True)

        # Generate filenames
        suffix = f"{bandwidth}.{'udp' if udp else 'tcp'}"
        if count != 0:
            suffix = f"{count}.{suffix}"

        self.server_log = os.path.join(
            file_out_dir, f"{file_base_name}.iperf3.{suffix}.server.log"
        )
        self.server_csv = os.path.join(
            file_out_dir, f"{file_base_name}.iperf3.{suffix}.server.csv"
        )
        self.client_log = os.path.join(
            file_out_dir, f"{file_base_name}.iperf3.{suffix}.client.log"
        )
        self.client_csv = os.path.join(
            file_out_dir, f"{file_base_name}.iperf3.{suffix}.client.csv"
        )

        self.server_process = None
        self.client_process = None

    def start(self) -> int:
        """Start iPerf3 server and client."""
        with self.lock:
            if self.running:
                print("[Iperf3Monitor] Already running")
                return False

            # Start iPerf3 server
            server_cmd = f"iperf3 -s -1 --logfile {self.server_log}"
            self.server_process = self.server.popen(server_cmd)
            # wait a small time
            time.sleep(2)

            # Start iPerf3 client
            client_cmd = (
                f"iperf3 -c {self.server.IP()} "
                f"{'-u ' if self.udp else ''}"
                f"-b {self.bandwidth} "
                f"-t {self.experiment_time} "
                f"-i {self.time_to_report} "
                f"--logfile {self.client_log}"
            )
            self.client_process = self.client.popen(client_cmd)

            self.running = True
        return self.experiment_time

    def stop(self):
        """Stop measurements and parse results."""
        with self.lock:
            if not self.running:
                print("[Iperf3Monitor] Not running")
                return False

            self.client_process.terminate()
            self.server_process.terminate()

            # Wait for processes to terminate
            time.sleep(1)

            # Parse output files
            self._parse_files_as_csv()

            self.running = False
        return True

    def _parse_files_as_csv(self):
        """Parse iPerf3 server and client text output into CSV files."""
        # Parse server log
        if os.path.exists(self.server_log):
            with open(self.server_log, "r") as f:
                server_lines = f.readlines()
            self._parse_iperf3_text_output_server(server_lines, self.server_csv)

        # Parse client log
        if os.path.exists(self.client_log):
            with open(self.client_log, "r") as f:
                client_lines = f.readlines()
            self._parse_iperf3_text_output_client(client_lines, self.client_csv)

    def _parse_iperf3_text_output_server(self, lines, output_csv):
        """Parse iPerf3 text output into CSV format."""
        intervals = []
        current_interval = {}

        # These patterns match the different line formats in iPerf3 output
        interval_pattern = re.compile(
            r"\[\s*\d+\]\s+"
            r"(?P<start>\d+\.\d+)-(?P<end>\d+\.\d+)\s+sec\s+"
            r"(?P<transfer>\d+\.\d+)\s+[KM]?Bytes\s+"
            r"(?P<bitrate>\d+\.\d+)\s+[KM]?bits/sec\s+"
            r"(?P<jitter>\d+\.\d+)\s+ms\s+"
            r"(?P<lost>\d+)/(?P<total>\d+)\s+"
            r"\((?P<loss_percent>\d+)%\)"
        )

        summary_pattern = re.compile(
            r"\[\s*\d+\]\s+"
            r"(?P<start>\d+\.\d+)-(?P<end>\d+\.\d+)\s+sec\s+"
            r"(?P<transfer>\d+\.\d+)\s+[KM]?Bytes\s+"
            r"(?P<bitrate>\d+\.\d+)\s+[KM]?bits/sec\s+"
            r"(?P<jitter>\d+\.\d+)\s+ms\s+"
            r"(?P<lost>\d+)/(?P<total>\d+)\s+"
            r"\((?P<loss_percent>\d+)%\)\s+receiver"
        )

        for line in lines:
            # Skip empty lines and header lines
            if not line.strip() or line.startswith("-") or "Interval" in line:
                continue

            # Try to match interval lines
            match = interval_pattern.search(line) or summary_pattern.search(line)
            if match:
                interval = {
                    "start": float(match.group("start")),
                    "end": float(match.group("end")),
                    "transfer_bytes": float(match.group("transfer")),
                    "transfer_units": "MBytes" if "MBytes" in line else "KBytes",
                    "bitrate": float(match.group("bitrate")),
                    "bitrate_units": "Mbits/sec" if "Mbits" in line else "Kbits/sec",
                    "jitter_ms": float(match.group("jitter")),
                    "lost_packets": int(match.group("lost")),
                    "total_packets": int(match.group("total")),
                    "loss_percent": int(match.group("loss_percent")),
                }
                intervals.append(interval)

        # Write to CSV
        if intervals:
            with open(output_csv, "w", newline="") as csvfile:
                fieldnames = [
                    "start_sec",
                    "end_sec",
                    "transfer_bytes",
                    "transfer_units",
                    "bitrate_bps",
                    "bitrate_units",
                    "jitter_ms",
                    "lost_packets",
                    "total_packets",
                    "loss_percent",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for interval in intervals:
                    # Convert transfer to consistent bytes unit
                    transfer_bytes = interval["transfer_bytes"]
                    if interval["transfer_units"] == "MBytes":
                        transfer_bytes *= 1024 * 1024
                    elif interval["transfer_units"] == "KBytes":
                        transfer_bytes *= 1024

                    # Convert bitrate to consistent bps unit
                    bitrate_bps = interval["bitrate"]
                    if interval["bitrate_units"] == "Mbits/sec":
                        bitrate_bps *= 1000000
                    elif interval["bitrate_units"] == "Kbits/sec":
                        bitrate_bps *= 1000

                    writer.writerow(
                        {
                            "start_sec": interval["start"],
                            "end_sec": interval["end"],
                            "transfer_bytes": transfer_bytes,
                            "transfer_units": interval["transfer_units"],
                            "bitrate_bps": bitrate_bps,
                            "bitrate_units": interval["bitrate_units"],
                            "jitter_ms": interval["jitter_ms"],
                            "lost_packets": interval["lost_packets"],
                            "total_packets": interval["total_packets"],
                            "loss_percent": interval["loss_percent"],
                        }
                    )

    def _parse_iperf3_text_output_client(self, lines, output_csv):
        """Parse iPerf3 client text output into CSV format."""
        intervals = []
        current_interval = {}

        # Patterns for client output (different from server)
        interval_pattern = re.compile(
            r"\[\s*\d+\]\s+"
            r"(?P<start>\d+\.\d+)-(?P<end>\d+\.\d+)\s+sec\s+"
            r"(?P<transfer>\d+\.\d+)\s+[KM]?Bytes\s+"
            r"(?P<bitrate>\d+\.\d+)\s+[KM]?bits/sec\s+"
            r"(?P<total>\d+)"
        )

        summary_pattern = re.compile(
            r"\[\s*\d+\]\s+"
            r"(?P<start>\d+\.\d+)-(?P<end>\d+\.\d+)\s+sec\s+"
            r"(?P<transfer>\d+\.\d+)\s+[KM]?Bytes\s+"
            r"(?P<bitrate>\d+\.\d+)\s+[KM]?bits/sec\s+"
            r"(?P<jitter>\d+\.\d+)\s+ms\s+"
            r"(?P<lost>\d+)/(?P<total>\d+)\s+"
            r"\((?P<loss_percent>\d+)%\)\s+sender"
        )

        for line in lines:
            # Skip empty lines and header lines
            if not line.strip() or line.startswith("-") or "Interval" in line:
                continue

            # Try to match interval lines first
            match = interval_pattern.search(line)
            if match:
                interval = {
                    "start": float(match.group("start")),
                    "end": float(match.group("end")),
                    "transfer_bytes": float(match.group("transfer")),
                    "transfer_units": "MBytes" if "MBytes" in line else "KBytes",
                    "bitrate": float(match.group("bitrate")),
                    "bitrate_units": "Mbits/sec" if "Mbits" in line else "Kbits/sec",
                    "total_packets": int(match.group("total")),
                    "jitter_ms": None,  # Client intervals don't show jitter
                    "lost_packets": None,
                    "loss_percent": None,
                }
                intervals.append(interval)
                continue

            # Try to match summary line (has additional info)
            match = summary_pattern.search(line)
            if match and intervals:
                # Update the last interval (summary) with additional metrics
                intervals[-1].update(
                    {
                        "jitter_ms": float(match.group("jitter")),
                        "lost_packets": int(match.group("lost")),
                        "loss_percent": int(match.group("loss_percent")),
                    }
                )

        # Write to CSV
        if intervals:
            with open(output_csv, "w", newline="") as csvfile:
                fieldnames = [
                    "start_sec",
                    "end_sec",
                    "transfer_bytes",
                    "transfer_units",
                    "bitrate_bps",
                    "bitrate_units",
                    "jitter_ms",
                    "lost_packets",
                    "total_packets",
                    "loss_percent",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for interval in intervals:
                    # Convert transfer to consistent bytes unit
                    transfer_bytes = interval["transfer_bytes"]
                    if interval["transfer_units"] == "MBytes":
                        transfer_bytes *= 1024 * 1024
                    elif interval["transfer_units"] == "KBytes":
                        transfer_bytes *= 1024

                    # Convert bitrate to consistent bps unit
                    bitrate_bps = interval["bitrate"]
                    if interval["bitrate_units"] == "Mbits/sec":
                        bitrate_bps *= 1000000
                    elif interval["bitrate_units"] == "Kbits/sec":
                        bitrate_bps *= 1000

                    writer.writerow(
                        {
                            "start_sec": interval["start"],
                            "end_sec": interval["end"],
                            "transfer_bytes": transfer_bytes,
                            "transfer_units": interval["transfer_units"],
                            "bitrate_bps": bitrate_bps,
                            "bitrate_units": interval["bitrate_units"],
                            "jitter_ms": interval["jitter_ms"],
                            "lost_packets": interval["lost_packets"],
                            "total_packets": interval["total_packets"],
                            "loss_percent": interval["loss_percent"],
                        }
                    )
