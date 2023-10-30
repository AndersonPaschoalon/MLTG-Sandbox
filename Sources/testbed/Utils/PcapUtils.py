import os
from scapy.all import *


class PcapUtils:

    @staticmethod
    def pcap_summarizer(pcap_file):
        """
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
        """
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
        return tx_bytes, time_sec, n_packets_tcp, n_packets_udp, n_packets_other