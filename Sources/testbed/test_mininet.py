from mininet.net import Mininet
from mininet.cli import CLI

net = Mininet()
net.addHost("h1")
net.addHost("h2")
net.addLink("h1", "h2")
net.start()
CLI(net)
net.stop()