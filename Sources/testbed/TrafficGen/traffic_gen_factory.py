from testbed.TrafficGen.iperf_tg import IperfGen
from testbed.TrafficGen.harpoon_tg import HarpoonGen

class TrafficGenFactory:
    @staticmethod
    def create(config):
        if config.type == "iperf":
            return IperfGen(config)
        elif config.type == "d-itg":
            return HarpoonGen(config)  # Future-proof
        else:
            raise ValueError("Unsupported traffic generator")