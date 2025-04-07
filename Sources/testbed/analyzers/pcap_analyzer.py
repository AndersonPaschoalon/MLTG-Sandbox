import csv
import json
import subprocess
from pathlib import Path
from typing import Dict, List

import pandas as pd


class PCAPAnalyzer:
    """Extracts packet-level and flow-level metrics from PCAPs without plotting"""

    @staticmethod
    def extract_packet_metrics(pcap_path: Path, output_csv: Path) -> None:
        """
        Extract per-packet metrics using tshark
        Output columns: pkt_count,flow_id,arrival_time,inter_arrival_time,pkt_size,protocol_stack
        """
        tshark_cmd = [
            "tshark",
            "-r",
            str(pcap_path),
            "-T",
            "fields",
            "-e",
            "frame.number",
            "-e",
            "tcp.stream",
            "-e",
            "udp.stream",
            "-e",
            "frame.time_epoch",
            "-e",
            "frame.time_delta",
            "-e",
            "frame.len",
            "-e",
            "frame.protocols",
            "-E",
            "header=y",
            "-E",
            "separator=,",
            "-E",
            "quote=d",
        ]

        with open(output_csv, "w") as f:
            subprocess.run(tshark_cmd, stdout=f, check=True)

        # Post-process to merge TCP/UDP flows
        df = pd.read_csv(output_csv)
        df["flow_id"] = df["tcp.stream"].combine_first(df["udp.stream"])
        df.drop(["tcp.stream", "udp.stream"], axis=1, inplace=True)
        df.to_csv(output_csv, index=False)

    @staticmethod
    def extract_flow_metrics(pcap_path: Path, output_json: Path) -> None:
        """
        Extract flow-level statistics using nfdump
        """
        cmd = f"nfdump -r {pcap_path} -o json > {output_json}"
        subprocess.run(cmd, shell=True, check=True)

    @staticmethod
    def analyze(pcap_dir: Path, output_dir: Path) -> Dict[str, Path]:
        """Run full analysis pipeline"""
        output_dir.mkdir(exist_ok=True)
        results = {}

        for pcap in pcap_dir.glob("*.pcap"):
            stem = pcap.stem
            # Packet-level analysis
            pkt_csv = output_dir / f"{stem}_packets.csv"
            PCAPAnalyzer.extract_packet_metrics(pcap, pkt_csv)

            # Flow-level analysis
            flow_json = output_dir / f"{stem}_flows.json"
            PCAPAnalyzer.extract_flow_metrics(pcap, flow_json)

            results[stem] = {"packet_metrics": pkt_csv, "flow_metrics": flow_json}

        return results
