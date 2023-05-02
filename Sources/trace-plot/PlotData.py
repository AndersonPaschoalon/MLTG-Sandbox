import numpy as np
from Database import TraceDatabase
from Database import RandomData
from Database import RandomData2
from Utils import Utils


class PlotData:

    def __init__(self, flow_database, name, color):
        self.flow_database = flow_database
        if flow_database == "random":
            print("Using random data - for test only")
            self.packet_table = RandomData()
        elif flow_database == "random2a":
            self.packet_table = RandomData2()
        elif flow_database == "random2b":
            self.packet_table = RandomData2(num_packets=120, seed=543421)
        else:
            self.packet_table = TraceDatabase(database_file=flow_database, trace_name=name)
        self.name = name
        self.color = color

    def load(self, cols):
        return self.packet_table.fetch(column=cols)

    def arrivals(self):
        return np.array(self.packet_table.fetch(column="ts"))

    def inter_arrivals(self):
        if "random2" in self.flow_database:
            arrival_times, pkt_sizes = self.packet_table.fetch()
            return Utils.calc_interarrival_times(arrival_times)
        else:
            ts = self.packet_table.fetch(column="ts")
            inter_arrivals = Utils.diff(ts)
            return np.array(inter_arrivals)

    def packet_sizes(self):
        if "random2" in self.flow_database:
            arrival_times, pkt_sizes = self.packet_table.fetch()
            return pkt_sizes
        else:
            return np.array(self.packet_table.fetch(column="pktSize"))

    def arrival_times_and_pkt_sizes(self):
        if "random2" in self.flow_database:
            arrival_times, pkt_sizes = self.packet_table.fetch()
            return arrival_times, pkt_sizes
        else:
            arrivals = np.array(self.packet_table.fetch(column="ts"))
            pkt_sizes = np.array(self.packet_table.fetch(column="pktSize"))
            return arrivals, pkt_sizes






