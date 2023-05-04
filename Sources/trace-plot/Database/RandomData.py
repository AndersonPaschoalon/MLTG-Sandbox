import numpy as np
import math
import json
import random
from Utils import Utils
from scipy.stats import pareto


class RandomData:

    def __init__(self, database_file, name,
                 config_str='{"seed": 42, "n_packets": 1000, "n_flows": 10}', color="blue"):
        """
        Gerenate random data to test the plots.
        :param database_file: For the database files, the available values are:
        weibull(default), 3spikes.
        :param name: Trace name, used in the plots as labels.
        :param config: For the config dictionary the available values are:
        seed, n_packets, n_flows, seed.
        """
        self.database_file = database_file
        self.name = name
        self.config = json.loads(config_str)
        self.color = color
        # np.random.seed(self.config["seed"])
        self.n_packets = self.config["n_packets"]
        self.n_flows = self.config["n_flows"]
        self.seed = self.config["seed"]
        print(f"Database file {self.database_file}...")
        if self.database_file == "3spikes":
            #
            # 3spikes
            #
            np_arrival_times, np_packet_sizes = self._3spikes_arrival_times_and_pkt_sizes(num_packets=self.n_packets,
                                                                                          seed=self.seed)
            self.np_arrival_times = np_arrival_times
            self.np_packet_sizes = np_packet_sizes
            self.np_inter_arrival_times = Utils.diff(self.np_arrival_times)
        else:
            #
            # stochastic distributions
            #
            if self.database_file == "normal":
                self.np_inter_arrival_times = RandomData.sample_mod_normal_fix(self.n_packets)
            elif self.database_file == "exponential":
                self.np_inter_arrival_times = RandomData.sample_exponential_fix(self.n_packets)
            elif self.database_file == "pareto":
                self.np_inter_arrival_times = RandomData.sample_pareto_fix(self.n_packets)
            else:
                # weibull
                self.np_inter_arrival_times = RandomData.sample_weibull_fix(self.n_packets)

            # arrival times
            arrivals = []
            acc = 0
            for val in self.np_inter_arrival_times:
                acc = val + acc
                arrivals.append(acc)
            self.np_arrival_times = np.array(arrivals)

            # packet sizes
            self.np_packet_sizes = RandomData.sample_uniform(n=self.n_packets, min_val=64, max_val=1518)

        # packet id
        self.np_packet_id = np.array(list(range(1, self.n_packets)))

        # tsSec
        ts_sec = []
        for val in self.np_arrival_times:
            ts_sec.append(int(math.ceil(val)))
        self.np_ts_sec = np.array(ts_sec)

        # tsUsec
        ts_usec = []
        for arrival in self.np_arrival_times:
            arrivals_usec = (arrival - math.ceil(arrival)) * 1e6
            ts_usec.append(arrivals_usec)
        self.np_ts_usec = np.array(ts_usec)

        # time to live
        self.np_time_to_live = RandomData.sample_uniform(n=self.n_packets, min_val=50, max_val=80)

        # trace ID
        self.np_trace_id = np.ones(self.n_packets)

        # flow ID
        # self.np_flow_id = RandomData.sample_uniform(n=self.n_packets, min_val=1, max_val=self.n_flows)
        self.np_flow_id = RandomData.sample_flow_ids(self.n_packets)

    def load(self, labels_array):
        ret_dic = {}
        for label in labels_array:
            print(f"Loading {label}...")
            if label == "inter-arrival-times":
                ret_dic[label] = self.np_inter_arrival_times
            elif label == "arrival-times":
                ret_dic[label] = self.np_arrival_times
            elif label == "pktSize":
                ret_dic[label] = self.np_packet_sizes
            elif label == "packetID":
                ret_dic[label] = self.np_packet_id
            elif label == "tsSec":
                ret_dic[label] = self.np_ts_sec
            elif label == "tsUsec":
                ret_dic[label] = self.np_ts_usec
            elif label == "timeToLive":
                ret_dic[label] = self.np_time_to_live
            elif label == "traceID":
                ret_dic[label] = self.np_trace_id
            elif label == "flowID":
                ret_dic[label] = self.np_flow_id
            else:
                ret_dic[label] = []
        return ret_dic

    @staticmethod
    def sample_mod_normal(n, mean, std):
        samples = np.abs(np.random.normal(mean, std, n))
        return samples

    @staticmethod
    def sample_weibull(n, shape, scale):
        sample = np.random.weibull(shape, size=n)
        sample = sample * scale
        return sample

    @staticmethod
    def sample_exponential(n, mean):
        scale = 1.0 / mean
        samples = np.random.exponential(scale, n)
        return samples

    @staticmethod
    def sample_pareto(n, mean):
        # Estimate shape parameter
        b = abs(mean / (mean - 1))
        # Generate samples from Pareto distribution
        samples = pareto.rvs(b, size=n)
        return samples

    @staticmethod
    def sample_uniform(n, min_val, max_val):
        return np.random.randint(min_val, max_val, size=n).tolist()

    @staticmethod
    def sample_mod_normal_fix(n):
        mean = 0
        std = 0.1
        samples = np.abs(np.random.normal(mean, std, n))
        return samples

    @staticmethod
    def sample_weibull_fix(n=100):
        shape = 1.5
        scale = 0.075
        return RandomData.sample_weibull(n, shape, scale)

    @staticmethod
    def sample_exponential_fix(n):
        return RandomData.sample_exponential(n, 25.0)

    @staticmethod
    def sample_pareto_fix(n):
        return RandomData.sample_pareto(n, 1.01)

    @staticmethod
    def sample_flow_ids(n_values):
        flow_ids = [1]  # Start with 1
        for _ in range(n_values - 1):
            prev_id = flow_ids[-1]
            next_id = random.choice(list(range(1, prev_id + 1)) + [prev_id + 1])
            flow_ids.append(next_id)
        return flow_ids

    @staticmethod
    def _3spikes_arrival_times_and_pkt_sizes(num_packets=30, seed=42):
        np.random.seed(seed)
        # Generate interarrival times with spikes
        arrival_times = []
        packet_sizes = []

        # Spike 1 (around 1 second)
        spike1_start = 1
        spike1_end = 3
        spike1_packets = int(num_packets * 0.3)
        arrival_times.extend(np.random.uniform(spike1_start, spike1_end, spike1_packets))
        packet_sizes.extend(np.random.randint(1, 20, spike1_packets))

        # Spike 2 (around 7 seconds)
        spike2_start = 7
        spike2_end = 9
        spike2_packets = int(num_packets * 0.3)
        arrival_times.extend(np.random.uniform(spike2_start, spike2_end, spike2_packets))
        packet_sizes.extend(np.random.randint(1, 20, spike2_packets))

        # Spike 3 (around 20 seconds)
        spike3_start = 20
        spike3_end = 22
        spike3_packets = int(num_packets * 0.3)
        arrival_times.extend(np.random.uniform(spike3_start, spike3_end, spike3_packets))
        packet_sizes.extend(np.random.randint(1, 20, spike3_packets))

        # Sparse packets outside the spikes
        spikeS_start = 0
        spikeS_end = 60
        spikeS_packets = int(num_packets * 0.1)
        arrival_times.extend(np.random.uniform(spikeS_start, spikeS_end, spikeS_packets))
        packet_sizes.extend(np.random.randint(1, 20, spikeS_packets))

        np_arrival_times = np.array(arrival_times)
        np_packet_sizes = np.array(packet_sizes)
        sort_indices = np.argsort(np_arrival_times)
        np_arrival_times = np_arrival_times[sort_indices]
        np_packet_sizes = np_packet_sizes[sort_indices]

        return np_arrival_times, np_packet_sizes


if __name__ == '__main__':
    cfg_str = '{"seed": 42, "n_packets": 20, "n_flows": 5}'
    rd = RandomData(database_file="weibull", name="test", config_str=cfg_str)
    all_labels = ["inter-arrival-times", "arrival-times", "packetID", "traceID", "flowID", "tsSec", "tsUsec", "pktSize",
                  "timeToLive"]
    all_data = rd.load(all_labels)
    print(all_data)


