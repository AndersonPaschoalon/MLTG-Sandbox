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
from NetQA.PingMeasurer import PingMeasurer

def single_hop_topo():
    SingleHopTopo.simple_test()
    net, topo = SingleHopTopo.initialize()
    print("*********************************************************")
    print("** Starting Mininet CLI ...")
    print("*********************************************************")
    CLI(net)
    SingleHopTopo.finalize(net)

def test_iperf_gen():
    # Parameters
    pcap_sample = "../../Pcap/SkypeIRC.cap.pcap"
    out_dir = "_Tests"
    experiment_name = "Abacate"
    display_cli = True
    cloud_loss = 0.01
    cloud_delay = '20ms'
    run_capture = True
    run_qa = True
    OSUtils.__debug_mode__ = True


    # Prepare eviroment
    experiment_dir = os.path.join(out_dir, experiment_name)
    OSUtils.create_directory(experiment_dir)
    if not os.path.exists(experiment_dir):
        print(f"Pcap file {pcap_sample} does not exist!")
        return False

    # create network
    net, topo = SingleHopTopo.initialize(cloud_loss=cloud_loss, cloud_delay=cloud_delay)
    h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
    h1_cfg = {
        "if": "h1-eth0",
    }
    h3_cfg = {
        "if": "h3-eth0",
    }
    # OSUtils.breakpoint("@ _tests.py")
    if display_cli:
        CLI(net)

    # define iperf traffic generator
    client_log = os.path.join(experiment_dir, "iperf-client")
    server_log = os.path.join(experiment_dir, "iperf-server")
    iperf = IperfGen(pcap=pcap_sample, client=h1, server=h3,
                     client_cfg=h1_cfg, server_cfg=h3_cfg, verbose=True, 
                     client_log=client_log, server_log=server_log)
    traffic_generators = [iperf]

    #
    # Trace Capture
    #
    if run_capture:
        # Run capture tests
        tcpdump = TcpdumpWrapper(verbose=True)
        for tg in traffic_generators:
            # init vars
            out_file = os.path.join(experiment_dir, f"capture.host1.{tg.name()}")
            tcpdump_log = os.path.join(experiment_dir, f"capture.host1.{tg.name()}")

            # start server
            print(f"Starting {tg.name()} server...")
            tg.server_listen()

            # start capture
            print(f"Starting capture on host1...")
            tcpdump.start(mn_host=h1, interface="h1-eth0", pcap_file=out_file, log_file=tcpdump_log)

            # start traffic generation
            print(f"Starting {tg.name()} traffic generation...")
            time_to_wait = tg.client_start()

            # wait to finish
            print(f"Waiting {time_to_wait}s")
            # time.sleep(time_to_wait)
            time.sleep(15)

            # stop capture
            time.sleep(2)
            tg.client_stop()
            tcpdump.stop()
            tg.server_stop()

    #
    # QA analysis
    #
    if run_qa:
        # run network quality tests
        result_file = os.path.join(out_dir, experiment_name, "qa_result.txt")
        measurer = PingMeasurer(h4.IP(), 1, 60, result_file)
        for tg in traffic_generators:
            # start server
            print(f"Starting {tg.name()} server...")
            tg.server_listen()

            # start traffic generation
            print(f"Starting {tg.name()} traffic generation...")
            time_to_wait = tg.client_start()

            # start QA
            measurer.start(h3)

            # wait to finish
            print(f"Waiting {time_to_wait}s")
            # time.sleep(60)
            time.sleep(10)

            # stop capture
            time.sleep(2)
            tg.client_stop()
            tg.server_stop()

    SingleHopTopo.finalize(net)

    print(f"Experiment {experiment_name} finalized successfully!")
    return True


if __name__ == '__main__':
    test01 = False
    test02 = True
    test03 = False
    test04 = False
    test05 = False
    test06 = False
    test07 = False
    test08 = False

    if test01: single_hop_topo()
    if test02: test_iperf_gen()



