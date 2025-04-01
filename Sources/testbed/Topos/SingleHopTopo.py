import os
import time

from logger.logger import Logger
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
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

    _controller = ""
    _log_controller = "single_hop_topo.controller.log"
    _controller_port = 6653


    def __init__(self, cloud_loss=0.01, cloud_delay='20ms'):
        """
        Create a Single Hop Network
        """

        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        self.host1 = self.addHost('h1', protocols='OpenFlow13')
        self.host2 = self.addHost('h2', protocols='OpenFlow13')
        self.host3 = self.addHost('h3')
        self.host4 = self.addHost('h4')
        self.switch1 = self.addSwitch('s1')
        self.switch2 = self.addSwitch('s2')
        # Add links
        self.addLink(self.host1, self.switch1)
        self.addLink(self.host2, self.switch1)
        self.addLink(self.host3, self.switch2)
        self.addLink(self.host4, self.switch2)

        self.addLink(self.switch1, self.switch2, delay=cloud_delay, loss=cloud_loss)

    @staticmethod
    def initialize(controller="ovs-testcontroller", cloud_loss=0.01, cloud_delay='20ms'):
        """
        Method to create the topology, initialize the network and the controller,
        and add the rulles for the executing topology.
        """
        SingleHopTopo._controller = controller
        setLogLevel('info')
        os.system("sudo mn -c")
        topo = SingleHopTopo(cloud_loss=cloud_loss, cloud_delay=cloud_delay)
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
            log_file = os.path.join(Logger.log_dir(), SingleHopTopo._log_controller)
            OSUtils.run(f"sudo ovs-testcontroller ptcp:6653  >{log_file}2>&1 &", new_console=True)
            print("Wait ovs-testcontroller to be set up...")
            time.sleep(6)
            # Verify controller is running
            if not OSUtils.check_port_open(6653):
                raise RuntimeError("Controller failed to start!")
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
        if str(SingleHopTopo._controller).lower() == "opendaylight":
            print("not implemented")
        else:
            os.system("killall ovs-testcontroller")


if __name__ == '__main__':
    SingleHopTopo.simple_test()
    net, topo = SingleHopTopo.initialize()
    print("*********************************************************")
    print("** Starting Mininet CLI ...")
    print("*********************************************************")
    CLI(net)
    SingleHopTopo.finalize(net)


