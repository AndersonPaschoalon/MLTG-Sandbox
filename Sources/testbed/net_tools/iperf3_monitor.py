import os
import threading

from mininet.node import Host
from mininet.util import custom, decode, waitListening

from testbed.utils.mininet_utils import MininetUtils


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
        interface_index_client: int = 0,  # Default to first interface
        interface_index_server: int = 0,  # Default to first interface
        count: int = 0,
    ):
        """
        client: iperf3 client
        server: iperf3 server
        file_out_dir: out dir where the files will be saved
        file_base_name: base file name used in the generated files
        bandwidth: bandwidth used in this experiment
        time_to_report: time to report used in this experiment
        count: just a count to avoid conflict on file names on testing.
        """
        self.lock = threading.Lock()
        self.running = False
        self.client = client
        self.server = server
        self.bandwidth = bandwidth
        self.time_to_report = time_to_report
        self.experiment_time = experiment_time
        if count != 0:
            file_server_log = f"{file_base_name}.{count}.iperf3.{bandwidth}.server.log"
            file_server_csv = f"{file_base_name}.{count}.iperf3.{bandwidth}.server.csv"
            file_client_log = f"{file_base_name}.{count}.iperf3.{bandwidth}.client.log"
            file_client_csv = f"{file_base_name}.{count}.iperf3.{bandwidth}.client.csv"
        else:
            file_server_log = f"{file_base_name}.iperf3.{bandwidth}.server.log"
            file_server_csv = f"{file_base_name}.iperf3.{bandwidth}.server.csv"
            file_client_log = f"{file_base_name}.iperf3.{bandwidth}.client.log"
            file_client_csv = f"{file_base_name}.iperf3.{bandwidth}.client.csv"
        self.server_log = os.path.join(file_out_dir, file_server_log)
        self.client_log = os.path.join(file_out_dir, file_client_log)
        self.server_csv = os.path.join(file_out_dir, file_server_csv)
        self.client_csv = os.path.join(file_out_dir, file_client_csv)

    def star(self):
        with self.lock:
            if self.running:
                print(f"[Iperf3Monitor] Already running")
                return False
        # Get interface name (e.g., h1-eth0) using MininetUtils
        ip_server = self.server.IP()
        # TODO
        # - run the server command `iperf3 -s` (save the output in the server_log file)
        # - wait a small time just to make sure the server is up
        # - run the client comman d `iperf3 -c server_ip -u -b bandwidth -t  experiment_time -i time_to_report`
        # note: use mininet popen() so this command is non-bloking

    def wait(self):
        # if running, wait the experiment time. otherwise raise an exeption.
        # this is need becase we might want to do something after startting the experiment
        ...

    def stop(self):
        with self.lock:
            if self.running:
                print(f"[iperf3] Already running")
                return False
        # TODO
        # kill the client self.clinet.terminate()
        # wait a little bit
        # kill the server
        # run self._parse_files_as_csv()

    def _parse_files_as_csv(self):
        # TODO
        # basically parse the output files frm client and server into csv format
        ...


# Commands
# server iperf3 -s
# client iperf3 -c server_ip -u -b bandwidth -t -i time_to_report
# i: report every second

import csv
import json
import os
import threading
import time
from pathlib import Path

from mininet.node import Host
from mininet.util import waitListening


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
        interface_index_client: int = 0,
        interface_index_server: int = 0,
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

    def start(self):
        """Start iPerf3 server and client."""
        with self.lock:
            if self.running:
                print("[Iperf3Monitor] Already running")
                return False

            # Start iPerf3 server
            server_cmd = f"iperf3 -s -1 --logfile {self.server_log}"
            self.server_process = self.server.popen(server_cmd, shell=True)

            # Wait for server to start
            waitListening(server=self.server, port=5201, timeout=5)

            # Start iPerf3 client
            client_cmd = (
                f"iperf3 -c {self.server.IP()} "
                f"{'-u ' if self.udp else ''}"
                f"-b {self.bandwidth} "
                f"-t {self.experiment_time} "
                f"-i {self.time_to_report} "
                f"--logfile {self.client_log}"
            )
            self.client_process = self.client.popen(client_cmd, shell=True)

            self.running = True
            return True

    def wait(self):
        """Wait for the experiment to complete."""
        if not self.running:
            raise RuntimeError("Experiment not running")

        # Wait for client to finish (with some buffer time)
        time.sleep(self.experiment_time + 5)

        # Verify processes completed
        if self.client_process.poll() is None:
            print("[Warning] Client process did not complete")
        if self.server_process.poll() is None:
            print("[Warning] Server process did not complete")

    def stop(self):
        """Stop measurements and parse results."""
        with self.lock:
            if not self.running:
                print("[Iperf3Monitor] Not running")
                return False

            # Terminate processes if still running
            if self.client_process and self.client_process.poll() is None:
                self.client_process.terminate()
            if self.server_process and self.server_process.poll() is None:
                self.server_process.terminate()

            # Wait for processes to terminate
            time.sleep(1)

            # Parse output files
            self._parse_files_as_csv()

            self.running = False
            return True

    def _parse_files_as_csv(self):
        """Parse iPerf3 JSON output into CSV files."""
        # Parse server log
        if os.path.exists(self.server_log):
            with open(self.server_log) as f:
                server_data = json.load(f)
            self._write_csv(server_data, self.server_csv, is_server=True)

        # Parse client log
        if os.path.exists(self.client_log):
            with open(self.client_log) as f:
                client_data = json.load(f)
            self._write_csv(client_data, self.client_csv, is_server=False)

    def _write_csv(self, data, csv_path, is_server):
        """Write iPerf3 data to CSV file."""
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(
                [
                    "timestamp",
                    "interval",
                    "transfer_bytes",
                    "transfer_bits",
                    "bandwidth_bps",
                    "jitter_ms",
                    "lost_packets",
                    "total_packets",
                    "loss_percent",
                ]
            )

            # Extract relevant data
            if is_server:
                intervals = data.get("intervals", [])
            else:
                intervals = data.get("end", {}).get("sum", {}).get("intervals", [])
                if not intervals:  # Handle different iPerf3 versions
                    intervals = data.get("intervals", [])

            # Write interval data
            for interval in intervals:
                stream = interval.get("streams", [{}])[0]
                sum_data = interval.get("sum", {})

                # Use sum data if available, otherwise stream data
                data_source = sum_data if sum_data else stream

                writer.writerow(
                    [
                        interval.get("timestamp"),
                        f"{interval.get('start', 0):.1f}-{interval.get('end', 0):.1f}",
                        data_source.get("bytes", 0),
                        data_source.get("bits", 0),
                        data_source.get("bps", 0),
                        data_source.get("jitter_ms", 0),
                        data_source.get("lost_packets", 0),
                        data_source.get("packets", 0),
                        data_source.get("lost_percent", 0),
                    ]
                )
