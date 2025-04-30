import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from commons.connectors.alchemy_connector import AlchemyConnector
from commons.os.os_utils import OSUtils as osutils


class SnifferWrapper:

    def __init__(
        self,
        out_dir: str,
        experiment_name: str,
        driver: str = "libpcap",
        link_type: str = "ethernet",
        device_type: str = "pcap",
    ):
        """
        Initialize the sniffer wrapper.

        Args:
            out_dir: Directory where output will be saved
            experiment_name: Base name for experiment files
            driver: Sniffer driver type (default: libpcap)
            link_type: Link layer type (default: ethernet)
            device_type: Device type (default: pcap)
        """
        self.out_dir = os.path.abspath(out_dir)
        self.experiment_name = experiment_name
        self.driver = driver
        self.link_type = link_type
        self.device_type = device_type

        # Verify sniffer binary exists
        self.sniffer_path = os.path.abspath("sniffer/bin/sniffer.exe")
        if not os.path.exists(self.sniffer_path):
            raise FileNotFoundError(f"Sniffer binary not found at {self.sniffer_path}")

        # Create output directory if it doesn't exist
        os.makedirs(self.out_dir, exist_ok=True)

    def exec(self, device: str) -> Optional[str]:
        """
        Execute the sniffer with the given device/pcap file.

        Args:
            device: Path to pcap file to analyze

        Returns:
            None if successful, raises exception on failure
        """
        # Verify device file exists
        if not os.path.exists(device):
            raise FileNotFoundError(f"Device/pcap file not found: {device}")

        # Get absolute path of device
        device_abs = os.path.abspath(device)

        # Generate name parameter
        name = SnifferWrapper.trace_entry_name(self.experiment_name, device)

        # Build command
        cmd_sniffer = [
            self.sniffer_path,
            "--name",
            name,
            "--type",
            self.device_type,
            "--device",
            device_abs,
            "--driver",
            self.driver,
            "--link",
            self.link_type,
        ]
        cmd_chmod = ["chmod", "-R", "777", os.path.join(self.out_dir, "db")]
        osutils.execute_command_at(cmd_sniffer, self.out_dir, True)
        osutils.execute_command_at(cmd_chmod, self.out_dir, True)

    def list_loaded_traces(self) -> list:
        cmd = f"{self.sniffer_path} --show | awk '{{print $2}}'"
        stdout, _, _ = osutils.execute_command(cmd, cwd=self.out_dir)
        experiments = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line or line == "traceName" or line.startswith("----"):
                continue
            experiments.append(line)
        return experiments

    def list_traces_by_experiment(self, experiment_name):
        ll = self.list_loaded_traces()
        lex = []
        l: str
        for l in ll:
            if l.startswith(experiment_name):
                lex.append(l)
        return lex

    def tracedb_connection_string(self):
        trace_db_file = os.path.join("db", "TraceDatabase.db")
        return SnifferWrapper._make_connection_string(
            os.path.join(self.out_dir, trace_db_file)
        )

    def flowdb_connection_string(self, trace_name: str):
        trace_name_db = trace_name.rstrip(".pcap")
        flow_db_file = f"{trace_name_db}_Flow.db"
        return SnifferWrapper._make_connection_string(
            os.path.join(self.out_dir, flow_db_file)
        )

    def tracedb_connector(self):
        return AlchemyConnector(self.tracedb_connection_string())

    def flowdb_connector(self, trace_name: str):
        return AlchemyConnector(self.flowdb_connection_string(trace_name))

    @staticmethod
    def _make_connection_string(db_file: str):
        return f"sqlite:///{db_file}"

    @staticmethod
    def trace_entry_name(experiment_name: str, pcap: str) -> str:
        """
        Generate trace entry name from experiment name and pcap filename.

        Args:
            experiment_name: Name of the experiment
            pcap: Path to pcap file

        Returns:
            Formatted trace entry name (e.g., "Banana.lanDiurnal.pcap")
        """
        pcap_filename = os.path.basename(pcap)
        return f"{experiment_name}.{pcap_filename}"
