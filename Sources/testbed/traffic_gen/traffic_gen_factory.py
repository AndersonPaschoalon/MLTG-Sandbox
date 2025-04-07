from testbed.traffic_gen.harpoon_tg import HarpoonGen
from testbed.traffic_gen.iperf_gen import IperfGen


class TrafficGenFactory:
    @staticmethod
    def create(config):
        if config.type == "iperf":
            return IperfGen(config)
        elif config.type == "d-itg":
            return HarpoonGen(config)  # Future-proof
        else:
            raise ValueError("Unsupported traffic generator")
