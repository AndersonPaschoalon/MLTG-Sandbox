import os
import time
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from Utils import Utils

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

    def __init__( self ):
        "Create cSingle Hop"

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        Host1 = self.addHost('h1', protocols='OpenFlow13')
        Host2 = self.addHost('h2', protocols='OpenFlow13')
        Host3 = self.addHost('h3')
        Host4 = self.addHost('h4')
        Switch1 = self.addSwitch('s1')
        Switch2 = self.addSwitch('s2')
        # Add links
        self.addLink( Host1, Switch1)
        self.addLink( Host2, Switch1)
        self.addLink( Host3, Switch2)
        self.addLink( Host4, Switch2)

        self.addLink( Switch1, Switch2, delay='20ms', loss=0.01)

    @staticmethod
    def initialize():
        setLogLevel('info')
        os.system("sudo mn -c")
        topo = SingleHopTopo()
        Utils.run("sudo ovs-testcontroller ptcp:", new_console=True)
        print("wait ovs-testcontroller to be set up...")
        time.sleep(5)
        net = Mininet(topo=topo,
                      controller=None,
                      autoStaticArp=True)
        net.addController("c0",
                          controller=RemoteController,
                          ip=REMOTE_CONTROLLER_IP,
                          port=6653)
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
            os.system('mn -c')
            return True
        except AttributeError as error:
            print("Error executiong finalize(), net was not propperly defined")
            print(error)
            os.system('mn -c')
            return False


if __name__ == '__main__':
    SingleHopTopo.simple_test()
    net, topo = SingleHopTopo.initialize()
    print("*********************************************************")
    print("** Starting Mininet CLI ...")
    print("*********************************************************")
    CLI(net)
    SingleHopTopo.finalize(net)


