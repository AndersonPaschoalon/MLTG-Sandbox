import os
import time

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.topo import Topo
from mininet.util import dumpNodeConnections

from testbed.utils.os_utils import OSUtils


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

    REMOTE_CONTROLLER_IP = "127.0.0.1"

    def __init__(self, cloud_loss=0.01, cloud_delay="20ms"):
        """
        Create a Single Hop Network
        h1----+                    +----h3
              +--s1--========--s2--+
        h2----+                    +----h4
        """
        os.system("sudo mn -c")
        # Initialize topology
        Topo.__init__(self)
        # Add hosts and switches
        self.host1 = self.addHost("h1", protocols="OpenFlow13")
        self.host2 = self.addHost("h2", protocols="OpenFlow13")
        self.host3 = self.addHost("h3")
        self.host4 = self.addHost("h4")
        self.switch1 = self.addSwitch("s1")
        self.switch2 = self.addSwitch("s2")
        # Add links
        self.addLink(self.host1, self.switch1)
        self.addLink(self.host2, self.switch1)
        self.addLink(self.host3, self.switch2)
        self.addLink(self.host4, self.switch2)
        self.addLink(self.switch1, self.switch2, delay=cloud_delay, loss=cloud_loss)
        self.net = None

    def initialize(self, cloud_loss=0.01, cloud_delay="20ms"):
        """
        Method to create the topology, initialize the network and the controller.
        Now requires manual controller startup.
        """

        # topo = SingleHopTopo(cloud_loss=cloud_loss, cloud_delay=cloud_delay)
        self.net = Mininet(topo=self, controller=None, autoStaticArp=True)

        ans = input("Kill pior instances of SDN controllers? (y/n) > ").lower()
        if ans == "y":
            print("Kill any instance of ovs-testcontroller")
            OSUtils.run(
                'pid_proc="`sudo lsof -i:6653 |grep "ovs-testc" |awk \'{print($2)}\'`"; [ "$pid_proc" != "" ] && sudo kill $pid_proc'
            )

        print(f"\n=== Controller Setup ===")
        print(f"Please start your controller manually in another terminal:")
        print(f"1. For ovs-testcontroller:")
        print(f"   sudo ovs-testcontroller ptcp:6653")
        print(f"2. For OpenDayLight:")
        print(f"   Edit and run Scripts/Shell/start_odl.sh")
        print(f"\nPress ENTER when controller is running...")
        input()  # Wait for user confirmation

        # Check common controller ports
        controller_ports = [6653, 6633]
        active_port = None

        for port in controller_ports:
            if OSUtils.check_port_open(port):
                active_port = port
                break

        if active_port:
            print(f"Found active controller on port {active_port}")
            self.net.addController(
                "c0",
                controller=RemoteController,
                ip=SingleHopTopo.REMOTE_CONTROLLER_IP,
                port=active_port,
            )
            self.net.start()
        else:
            raise RuntimeError(
                "No active controller detected!\n"
                "Please ensure one of these is running:\n"
                "1. ovs-testcontroller (port 6653)\n"
                "2. OpenDayLight (port 6653 or 6633)\n"
                "Then run this again."
            )
        return self.net

    def cli(self):
        if self.net:
            print("*********************************************************")
            print("** Starting Mininet CLI ...")
            print("*********************************************************")
            CLI(self.net)

    def __del__(self):
        """
        Destructor to clean up Mininet resources.
        Safely stops the network and cleans residual processes.
        """
        print("\n=== Cleaning up network resources ===")
        # 1. Try to stop the network properly
        if hasattr(self, "net") and self.net:
            try:
                print("Stopping Mininet network...")
                self.net.stop()
            except Exception as e:
                print(f"Error stopping network: {e}")
            finally:
                self.net = None
        # 2. Force clean any residual processes
        try:
            print("Cleaning residual Mininet processes...")
            os.system("sudo mn -c")
        except Exception as e:
            print(f"Error during mn cleanup: {e}")
        print("Cleanup complete.")

    def simple_test(self):
        print("Dumping host connections")
        dumpNodeConnections(self.net.hosts)
        print("Testing network connectivity")
        self.net.pingAll()
        print("== Test Completed ==")


if __name__ == "__main__":
    topo = SingleHopTopo()
    net = topo.initialize()
    h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
    topo.simple_test()

    def get_host_interfaces(host):
        interfaces = []
        # Get all interfaces of the host
        for intf in host.intfList():
            if not intf.name == "lo":  # Skip loopback interfaceh1.
                ip = host.IP(intf=intf.name)
                interfaces.append({"interface": intf.name, "ip": ip})
        return interfaces

    for i in get_host_interfaces(h1):
        print(i)

    print("*********************************************************")
    print("** Starting Mininet CLI ...")
    print("*********************************************************")
    topo.cli()
    time.sleep(3)
