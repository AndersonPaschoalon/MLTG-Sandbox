import time
from mininet.net import Mininet
from mininet.node import Host, Switch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.link import OVSLink
from Topos.SingleHopTopo import SingleHopTopo
from Utils.MininetUtils import MininetUtils

"""
This script should be responsible for building the topologies, and run the experiments.

All topologies and networks may can be managed with the following commands:
To start:
net, topo = SingleHopTopo.initialize()
To test:
SingleHopTopo.simple_test()
To finalize and clean up:
SingleHopTopo.finalize(net)

Any script can be run inside any host inside the network with the following command:
h1 = net.hosts[0]
...
h<n> = net.hosts[<n-1>]
h1.cmd(<command>)
h<n>.cmd(<command>)
"""

if __name__ == '__main__':
    print("oi, tudo bom?")
    print("kkkkkkkkkkkk")
    print("aaaaaaaaaaaaaaaaa")
    print("oi, tudo bom?")
    """
    # SingleHopTopo.simple_test()
    net, topo = SingleHopTopo.initialize()
    h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
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
    """