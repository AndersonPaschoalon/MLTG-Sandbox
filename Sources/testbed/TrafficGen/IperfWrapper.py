"""
import os
from scapy.all import *


def pcap_summarizer(pcap_file):
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


def summary_to_command(dst_ipaddr, src_ipaddr, tx_bytes, time_sec, n_packets_tcp, n_packets_udp):
    protocol = "" if (n_packets_tcp > n_packets_udp) else "-u"
    time_int = int(time_sec)
    return f"iperf -c {dst_ipaddr} -B {src_ipaddr} {protocol} -n {tx_bytes} -t {time_int}"


def pcap_to_iperf_cmd(pcap_file, dst_ipaddr, src_ipaddr):
    tx_bytes, time_sec, n_packets_tcp, n_packets_udp, n_packets_other = pcap_summarizer(pcap_file)
    return summary_to_command(dst_ipaddr, src_ipaddr, tx_bytes, time_sec, n_packets_tcp, n_packets_udp), time_sec


def iperf_server_cmd():
    return "iperf -s"


def iperf_kill_cmd():
    return "killall iperf"



if __name__ == '__main__':
    pcap_sample = "../../../Pcap/SkypeIRC.cap.pcap"
    #print("pcap_summarizer:", pcap_summarizer(pcap_sample))
    print(pcap_to_iperf_cmd(pcap_sample, "10.0.0.4", "10.0.0.1"))
"""