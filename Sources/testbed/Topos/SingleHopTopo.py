import os
import time
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from Utils.OSUtils import OSUtils


REMOTE_CONTROLLER_IP = "127.0.0.1"


class SingleHopTopo(Topo):
    """
    Single Hop topology.
    This topology is created to simulate background traffic. 
    The main elements of the topology are:
    h1: act as the source of the background traffic
    h4: act as a sink for the background traffic
    h2 and h3: Act as a pair client-server. Used to measure the interference of a 
    constant and realistic traffic on the network quality.
    Link Switch1-Switch2: emulate a network, with degradation parameters
    """

    def __init__(self):
        """
        Create a Single Hop Network
        """

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        host1 = self.addHost('h1', protocols='OpenFlow13')
        host2 = self.addHost('h2', protocols='OpenFlow13')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        # Add links
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch2)
        self.addLink(host4, switch2)

        self.addLink(switch1, switch2, delay='20ms', loss=0.01)

    @staticmethod
    def initialize(controller="ovs-testcontroller"):
        """
        Method to create the topology, initialize the network and the controller,
        and add the rulles for the executing topology.
        """
        setLogLevel('info')
        os.system("sudo mn -c")
        topo = SingleHopTopo()
        net = Mininet(topo=topo,
                      controller=None,
                      autoStaticArp=True)
        print(f"Using controller {controller}")
        if str(controller).lower() == "opendaylight":
            print("not implemented")
        else:
            print("Kill any instance of ovs-testcontroller")
            OSUtils.run('pid_proc="`sudo lsof -i:6653 |grep "ovs-testc" |awk \'{print($2)}\'`"; [ "$pid_proc" != "" ] && sudo kill $pid_proc')
            print("Run ovs-testcontroller")
            OSUtils.run("sudo ovs-testcontroller ptcp:", new_console=True)
            print("Wait ovs-testcontroller to be set up...")
            time.sleep(5)
            net.addController("c0",
                              controller=RemoteController,
                              ip=REMOTE_CONTROLLER_IP,
                              port=6653)
            # block all the traffic going to host1

        net.start()
        return net, topo

    @staticmethod
    def simple_test():
        # Create and test a simple network
        net, topo = SingleHopTopo.initialize()
        print("Dumping host connections")
        dumpNodeConnections(net.hosts)
        print("Testing network connectivity")
        net.pingAll()
        net.stop()

    @staticmethod
    def finalize(net):
        try:
            net.stop()
        except AttributeError as error:
            print(f"Error execution finalize(), net was not properly defined\n{error}")
        os.system('mn -c')


if __name__ == '__main__':
    SingleHopTopo.simple_test()
    net, topo = SingleHopTopo.initialize()
    print("*********************************************************")
    print("** Starting Mininet CLI ...")
    print("*********************************************************")
    CLI(net)
    SingleHopTopo.finalize(net)


