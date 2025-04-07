import os
from pathlib import Path
from typing import Tuple

from scapy.all import TCP, UDP, rdpcap
from scapy.packet import Packet

from testbed.utils.exceptions import InvalidPCAPError, PCAPNotFoundError


class PcapUtils:

    @staticmethod
    def pcap_summarizer(pcap_file: str) -> Tuple[int, float, int, int, int]:
        """
        Analyze PCAP file and return traffic statistics.

        Args:
            pcap_file: Path to PCAP file

        Returns:
            Tuple containing:
            - tx_bytes: Total transmission bytes
            - time_sec: Duration in seconds
            - n_packets_tcp: TCP packet count
            - n_packets_udp: UDP packet count
            - n_packets_other: Other protocol packet count

        Raises:
            PCAPNotFoundError: If file doesn't exist
            InvalidPCAPError: If file is empty/corrupted
        """
        pcap_path = Path(pcap_file)
        if not pcap_path.exists():
            raise PCAPNotFoundError(pcap_file)

        try:
            packets = rdpcap(str(pcap_path))
            if not packets:
                raise InvalidPCAPError(pcap_file, "empty file")

            start_time = min(p.time for p in packets)
            end_time = max(p.time for p in packets)

            counts = {TCP: 0, UDP: 0, "other": 0}

            for packet in packets:
                counts[TCP if TCP in packet else UDP if UDP in packet else "other"] += 1

            return (
                sum(len(p) for p in packets),  # tx_bytes
                float(end_time - start_time),  # time_sec
                counts[TCP],  # n_packets_tcp
                counts[UDP],  # n_packets_udp
                counts["other"],  # n_packets_other
            )

        except Exception as e:
            raise InvalidPCAPError(pcap_file, str(e)) from e


"""

import os

from scapy.all import *


class PcapUtils:

    @staticmethod
    def pcap_summarizer(pcap_file):
        ""
        Returns a tuple with the main parameters related with bandwidth of the pcap.
        (tx_bytes, time_sec, n_packets_tcp, n_packets_udp, n_packets_other)
        Where:
        tx_bytes: transmissin rate in bytes per seconds
        time_sec: duration of the pcap in seconds
        n_packets_tcp: number of TCP packets
        n_packets_udp: number of UDP packets
        n_packets_other: number of packets from other protocols
        :param pcap_file: pcap file name
        :return:
        ""
        start_time = None
        end_time = None
        time_sec = 0
        tx_bytes = 0
        n_packets_tcp = 0
        n_packets_udp = 0
        n_packets_other = 0
        # scan pcap here
        if os.path.exists(pcap_file):
            packets = rdpcap(pcap_file)
            for packet in packets:
                tx_bytes += len(packet)

                if start_time is None or packet.time < start_time:
                    start_time = packet.time
                if end_time is None or packet.time > end_time:
                    end_time = packet.time
                if TCP in packet:
                    n_packets_tcp += 1
                elif UDP in packet:
                    n_packets_udp += 1
                else:
                    n_packets_other += 1
            time_sec = float(end_time - start_time)
        else:
            print("Error: pcap file {pcap_file} not found!")
        return tx_bytes, time_sec, n_packets_tcp, n_packets_udp, n_packets_other"

"""
