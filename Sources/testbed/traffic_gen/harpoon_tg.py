from testbed.traffic_gen.traffic_gen import TrafficGen
from testbed.utils.mininet_utils import MininetUtils


class HarpoonGen(TrafficGen):

    def __init__(self, pcap, host_client, host_server, client_cfg, server_cfg, verbose):
        super().__init__(
            pcap, host_client, host_server, client_cfg, server_cfg, verbose
        )
        self.tg_name = "Harpoon"
        if self.verbose:
            print("Harpoon initialized")

    def name(self):
        return self.tg_name

    def server_listen(self):
        super().server_listen()

    def server_stop(self):
        super().server_stop()

    def client_start(self):
        ret = super().client_start()
        if ret >= 0:
            print("TODO")
        else:
            pass
        return ret

    def client_stop(self):
        super().client_stop()
