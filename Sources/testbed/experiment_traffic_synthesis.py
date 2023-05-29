import time
from mininet.net import Mininet
from mininet.node import Host, Switch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.link import OVSLink
from Topos.SingleHopTopo import SingleHopTopo
from Utils.MininetUtils import MininetUtils
from TrafficGen.TrafficGen import TrafficGen
from TrafficGen.IperfGen import IperfGen
from TcpdumpWrapper.TcpdumpWrapper import TcpdumpWrapper


def test_iperf_gen(pcap_file, output_dir):
    # pcap_sample = "../../Pcap/SkypeIRC.cap.pcap"

    # create topology
    net, topo = SingleHopTopo.initialize()
    h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]

    # define the traffic generators
    iperf = IperfGen(pcap=pcap_file, host_client=h1, host_server=h3, client_cfg={}, server_cfg={})
    tcpdump = TcpdumpWrapper()


    ip_address = h1.cmd('ifconfig | grep "inet " | awk \'{print $2}\'')
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>ip_address:", ip_address)
    print("*********************************")
    MininetUtils.cmd_async(mn_host=h1, command="sleep 10; touch h1-command")
    print("*********************************")
    h2.cmd('touch h2-command')
    print("*********************************")
    h3.cmd('touch h3-command')
    print("*********************************")
    h4.cmd('touch h4-command')
    time.sleep(15)

    SingleHopTopo.finalize(net)