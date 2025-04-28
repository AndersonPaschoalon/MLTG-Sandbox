from abc import ABC, abstractmethod

from mininet.net import Mininet
from mininet.node import Host, Switch

from commons.config.experiment_config import ExperimentConfig


class TrafficGen(ABC):

    def __init__(self, client, server, config: ExperimentConfig):
        super().__init__()
        self.client = client
        self.server = server
        self.pcap = config.pcap
        self.ip_client = self.client.IP()
        self.ip_server = self.server.IP()
        self.config = config
        self.name_str = str((type(self).__name__).strip("Gen")).lower()

    @abstractmethod
    def server_listen(self):
        pass

    @abstractmethod
    def client_start(self):
        pass

    @abstractmethod
    def server_stop(self):
        pass

    @abstractmethod
    def client_stop(self):
        pass

    def name(self):
        return self.name_str
