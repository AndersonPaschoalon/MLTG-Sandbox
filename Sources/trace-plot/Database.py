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
        shape = 1.5
        scale = 7.5
        return RandomData.sample_weibull(sample_size, shape, scale)

    @staticmethod
    def sample_uniform(n, min_val, max_val):
        return np.random.randint(min_val, max_val, size=n).tolist()


if __name__ == '__main__':
    pt = PacketTable(database_file="db/TestSkype_Flow.db", trace_name="TestSkype")
    packets = pt.fetch(column="flowID, tsSec, pktSize")
    print(packets)
    interarr = pt.fetch(column="ts")
    print(interarr)
