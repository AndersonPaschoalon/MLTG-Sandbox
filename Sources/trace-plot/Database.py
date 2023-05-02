import sqlite3
import numpy as np
import math
from itertools import accumulate
from Utils import Utils


class TraceDatabase:

    def __init__(self, database_file, trace_name, config=None):
        self.database_file = database_file
        self.trace_name = trace_name
        self.config = config

    def fetch(self, column, order_by="tsSec, tsUsec"):
        #calc_inter_arrivals = False
        #if column.strip() == "ts":
        #    column = "tsSec, tsUsec"
        #    calc_inter_arrivals = True
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        sql_query = f"SELECT {column} FROM Packets ORDER BY {order_by}"
        print(f"Execute {sql_query}");
        c.execute(sql_query)
        rows = c.fetchall()
        conn.close()
        #if calc_inter_arrivals:
        #    return self._arrival_times(rows)
        return np.array(rows)

    def _calc_arrival_times(self):
        t = self.fetch("tsSec, tsUsec")
        tsec = [row[0] for row in t]
        tusec = [row[1] for row in t]
        arrivals = np.array(tsec) + np.array(tusec) / 1000000.0
        return arrivals

    def load(self, labels_array: []):
        ret_dic = {}
        pkt_table_labels = ["packetID", "traceID", "flowID", "tsSec", "tsUsec", "pktSize", "timeToLive"]
        for label in labels_array:
            if label in pkt_table_labels:
                print(f"Loading {label} from PacketTable...")
                values = self.fetch(label)
                ret_dic[label] = values
            elif label == "arrival-times":
                values = self._calc_arrival_times()
                ret_dic[label] = values
            elif label == "inter-arrival-times":
                arrivals = self._calc_arrival_times()
                inter_arrivals = Utils.diff(arrivals)
                ret_dic[label] = np.array(inter_arrivals)
        return ret_dic


class RandomData:

    def __init__(self, database_file, trace_name, config=None):
        self.database_file = database_file
        self.trace_name = trace_name
        self.config = config
        if config is None:
            np.random.seed(42)
            self.n_packets = 1000
            self.n_flows = 10
            self.seed = 42
        else:
            np.random.seed(config["seed"])
            self.n_packets = config["n_packets"]
            self.n_flows = config["n_flows"]
            self.seed = config["seed"]
            if self.database_file == "3spikes":
                np_arrival_times, np_packet_sizes = self.arrival_times_and_pkt_sizes(num_packets=self.n_packets,
                                                                                     seed=self.seed)
                self.np_arrival_times = np_arrival_times
                self.np_packet_sizes = np_packet_sizes

    def load(self, labels_array):
        ret_dic = {}
        for label in labels_array:
            print(f"Loading {label}...")
            if label == "inter-arrival-times":
                if self.database_file == "3spikes":
                    print(f"Using data 3spikes...")
                    ret_dic[label] = Utils.diff(self.np_arrival_times)
                else:
                    ret_dic[label] = RandomData.sample_weibull2(self.n_packets)
            elif label == "arrival-times":
                data = self.load(["inter-arrival-times"])
                inter_arrivals = data["inter-arrival-times"]
                arrivals = []
                acc = 0
                for val in inter_arrivals:
                    acc = val + acc
                    arrivals.append(acc)
                ret_dic[label] = np.array(arrivals)
            elif label == "pktSize":
                if self.database_file == "3spikes":
                    print(f"Using data 3spikes...")
                    ret_dic[label] = self.np_packet_sizes
                else:
                    ret_dic[label] = RandomData.sample_uniform(n=self.n_packets, min_val=64, max_val=1518)
            elif label == "packetID":
                ret_dic[label] = np.array(list(range(1, self.n_packets)))
            elif label == "tsSec":
                data = self.load(["arrival-times"])
                ts = data["arrival-times"]
                array = []
                for val in ts:
                    array.append(int(math.ceil(val)))
                ret_dic[label] = array
            elif label == "tsUsec":
                array = []
                data = self.load(["arrival-times"])
                arrivals = data["arrival-times"]
                for arrival in arrivals:
                    arrivals_usec = (arrival - math.ceil(arrival)) * 1e6
                    array.append(arrivals_usec)
                ret_dic[label] = np.array(array)
            elif label == "timeToLive":
                ret_dic[label] = RandomData.sample_uniform(n=self.n_packets, min_val=50, max_val=80)
            elif label == "traceID":
                ret_dic[label] = np.ones(self.n_packets)
            elif label == "flowID":
                ret_dic[label] = RandomData.sample_uniform(n=self.n_packets, min_val=1, max_val=self.n_flows)
            else:
                ret_dic[label] = []
        return ret_dic

    @staticmethod
    def sample_weibull(n, shape, scale):
        sample = np.random.weibull(shape, size=n)
        sample = sample * scale
        return sample

    @staticmethod
    def sample_weibull2(sample_size=100):
        shape = 1.5
        scale = 0.075
        return RandomData.sample_weibull(sample_size, shape, scale)

    @staticmethod
    def sample_uniform(n, min_val, max_val):
        return np.random.randint(min_val, max_val, size=n).tolist()

    @staticmethod
    def arrival_times_and_pkt_sizes(self, num_packets=30, seed=42):
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
    config = {"seed": 42, "n_packets": 100, "n_flows": 10}
    rd = RandomData(database_file="test", trace_name="test", config=config)
    all_labels = ["inter-arrival-times", "arrival-times", "packetID", "traceID", "flowID", "tsSec", "tsUsec", "pktSize", "timeToLive"]
    all_data = rd.load(all_labels)
    print(all_data)