import sqlite3
import numpy as np


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
            return self._inter_arrival_times(rows)
        return np.array(rows)

    def _inter_arrival_times(self, t):
        tsec = [row[0] for row in t]
        tusec = [row[1] for row in t]
        inter_arrivals = np.array(tsec) + np.array(tusec) / 1000000.0
        return inter_arrivals




if __name__ == '__main__':

    pt = PacketTable(database_file="db/TestSkype_Flow.db", trace_name="TestSkype")
    packets = pt.fetch(column="flowID, tsSec, pktSize")
    print(packets)
    interarr = pt.fetch(column="ts")
    print(interarr)
