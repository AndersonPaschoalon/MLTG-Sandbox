import sqlite3
import numpy as np
from Utils import Utils


class TraceDatabase:

    def __init__(self, database_file, name, config=None, color="blue"):
        self.database_file = database_file
        self.name = name
        self.config = config
        self.color = color

    def fetch(self, column, order_by="tsSec, tsUsec"):
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        sql_query = f"SELECT {column} FROM Packets ORDER BY {order_by}"
        print(f"Execute {sql_query}")
        c.execute(sql_query)
        rows = c.fetchall()
        conn.close()
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


