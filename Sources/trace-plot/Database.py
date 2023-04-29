import sqlite3
import numpy as np
from itertools import accumulate


class PacketTable:

    def __init__(self, database_file, trace_name):
        self.database_file = database_file
        self.trace_name = trace_name

    def fetch(self, column, order_by="tsSec, tsUsec"):
        calc_inter_arrivals = False
        if column.strip() == "ts":
            column = "tsSec, tsUsec"
            calc_inter_arrivals = True
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        sql_query = f"SELECT {column} FROM Packets ORDER BY {order_by}"
        print(f"Execute {sql_query}");
        c.execute(sql_query)
        rows = c.fetchall()
        conn.close()
        if calc_inter_arrivals:
            return self._arrival_times(rows)
        return np.array(rows)

    def _arrival_times(self, t):
        tsec = [row[0] for row in t]
        tusec = [row[1] for row in t]
        inter_arrivals = np.array(tsec) + np.array(tusec) / 1000000.0
        return inter_arrivals


class RandomData:

    def __init__(self):
        np.random.seed(42)

    def fetch(self, column, order_by="tsSec, tsUsec"):
        ret_list = []
        n_samples = 1000
        if column == "ts":
            inter_attivals = RandomData.sample_weibull2(n_samples)
            ret_list = list(accumulate(inter_attivals))
        elif column == "pktSize":
            ret_list = RandomData.sample_uniform(n=n_samples, min_val=64, max_val=1518)
        return ret_list

    @staticmethod
    def sample_weibull(n, shape, scale):
        sample = np.random.weibull(shape, size=n)
        sample = sample * scale
        return sample

    @staticmethod
    def sample_weibull2(sample_size=100):
        # shape = 1.5
        shape = 1.5
        # scale = 7.5
        scale = 0.075
        return RandomData.sample_weibull(sample_size, shape, scale)

    @staticmethod
    def sample_uniform(n, min_val, max_val):
        return np.random.randint(min_val, max_val, size=n).tolist()


class RandomData2:

    def __init__(self, num_packets=30, seed=42):
        self.num_packets = num_packets
        self.seed = seed

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

    def fetch(self, column=""):
        np_arrival_times, np_packet_sizes = self.arrival_times_and_pkt_sizes(num_packets=self.num_packets, seed=self.seed)
        return np_arrival_times, np_packet_sizes


if __name__ == '__main__':
    # pt = PacketTable(database_file="db/TestSkype_Flow.db", trace_name="TestSkype")
    # packets = pt.fetch(column="flowID, tsSec, pktSize")
    # print(packets)
    # interarr = pt.fetch(column="ts")
    # print(interarr)
    rd2 = RandomData2()
    np_arrival_times, np_packet_sizes = rd2.fetch()
    print("np_arrival_times:", np_arrival_times)
    print("np_packet_sizes:", np_packet_sizes)