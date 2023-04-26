import numpy as np
from Database import PacketTable
from Database import RandomData
from Utils import Utils


class PlotData:

    def __init__(self, flow_database, name, color):
        if flow_database == "random":
            print("Using random data - for test only")
            self.packet_table = RandomData()
        else:
            self.packet_table = PacketTable(database_file=flow_database, trace_name=name)
        self.name = name
        self.color = color

    def load(self, cols):
        return self.packet_table.fetch(column=cols)

    def arrivals(self):
        return np.array(self.packet_table.fetch(column="ts"))

    def inter_arrivals(self):
        ts = self.packet_table.fetch(column="ts")
        inter_arrivals = Utils.diff(ts)
        return np.array(inter_arrivals)

    def packet_sizes(self):
        return np.array(self.packet_table.fetch(column="pktSize"))






