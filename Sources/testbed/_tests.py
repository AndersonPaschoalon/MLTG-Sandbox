import os.path
import time
from mininet.net import Mininet
from mininet.node import Host, Switch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.link import OVSLink
from Topos.SingleHopTopo import SingleHopTopo
from Utils.MininetUtils import MininetUtils
from Utils.OSUtils import OSUtils
from TrafficGen.TrafficGen import TrafficGen
from TrafficGen.IperfGen import IperfGen
from TcpdumpWrapper.TcpdumpWrapper import TcpdumpWrapper


def test_iperf_gen():
    # Parameters
    pcap_sample = "../../Pcap/SkypeIRC.cap.pcap"
    out_dir = "test"
    experiment_name = "Abacate"
    OSUtils.__debug_mode__ = True

    # Prepare eviroment
    experiment_dir = os.path.join(out_dir, experiment_name)
    OSUtils.create_directory(experiment_dir)
    if not os.path.exists(experiment_dir):
        print(f"Pcap file {pcap_sample} does not exist!")
        return False

    # create network
    net, topo = SingleHopTopo.initialize()
    h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
    h1_cfg = {
        "if":"h1-eth0",
    }
    h3_cfg = {
        "if":"h3-eth0",
    }
    # CLI(net)
    OSUtils.breakpoint("@ _tests.py")

    # define iperf traffic generator
    iperf = IperfGen(pcap=pcap_sample, host_client=h1, host_server=h3,
                     client_cfg=h1_cfg, server_cfg=h3_cfg, verbose=True)
    tcpdump = TcpdumpWrapper(verbose=True)
    traffic_generators = [iperf]
    for tg in traffic_generators:
        # start server
        print(f"Starting {tg.name()} server...")
        tg.server_listen()
        # start capture
        print(f"Starting capture on host1...")
        out_file = os.path.join(experiment_dir, f"capture.host1.{tg.name()}")
        tcpdump.start(mn_host=h1, interface="h1-eth0", file=out_file)
        # start traffic generation
        print(f"Starting {tg.name()} traffic generation...")
        time_to_wait = tg.client_start()
        # wait to finish
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>", time_to_wait)
        time.sleep(50)
        # stop capture
        tg.client_stop()
        tcpdump.stop()
        tg.server_stop()
    SingleHopTopo.finalize(net)

    print(f"Experiment {experiment_name} finalized successfully!")
    return True


if __name__ == '__main__':
    test01 = True
    test02 = False
    test03 = False
    test04 = False
    test05 = False
    test06 = False
    test07 = False
    test08 = False

    if test01: test_iperf_gen()


