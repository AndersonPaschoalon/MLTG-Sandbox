import subprocess
import threading

from mininet.net import Mininet
from mininet.node import Host


class MininetUtils:

    @staticmethod
    def get_host_interfaces(host: Host):
        """Returns a list of interfaces and their IP addresses for a given host.

        Args:
            host (Host): The Mininet host object (e.g., h1, h2).

        Returns:
            list: A list of dictionaries containing interface names and IPs.
                Example: [{"interface": "h1-eth0", "ip": "10.0.0.1"}]
        """
        interfaces = []
        # Get all interfaces of the host
        for intf in host.intfList():
            if not intf.name == "lo":  # Skip loopback interface
                ip = host.IP(intf=intf.name)
                interfaces.append({"interface": intf.name, "ip": ip})
        return interfaces

    @staticmethod
    def get_host_interface(host: Host, index=0):
        """Returns the default interface (e.g., h1-eth0) and its IP.

        Args:
            host (Host): The Mininet host object.
            index (int, optional): Interface index (default: 0).

        Returns:
            dict: {"interface": "h1-eth0", "ip": "10.0.0.1"}
        """
        interfaces = MininetUtils.get_host_interfaces(host)
        if interfaces and len(interfaces) > index:
            return interfaces[index]
        return None
