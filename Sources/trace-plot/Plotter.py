import matplotlib.pyplot as plt
import pywt
import sqlite3
import numpy as np


class Plotter:

    @staticmethod
    def plot_bandwidth(trace_plots):
        plt.clf()
        fig, ax = plt.subplots()

        for trace_plot in trace_plots:
            conn = sqlite3.connect(trace_plot.flow_database_file)
            c = conn.cursor()
            # query = 'SELECT packetID, tsSec, tsUsec, pktSize FROM Packets WHERE traceId=? ORDER BY packetID'
            query = 'SELECT packetID, tsSec, tsUsec, pktSize FROM Packets WHERE traceId=? ORDER BY tsSec, tsUsec'
            c.execute(query, (trace_plot.trace_id,))
            rows = c.fetchall()

            times = []
            sizes = []
            last_time = None
            last_length = 0

            for row in rows:
                ts_sec = row[1]
                ts_usec = row[2]
                time = ts_sec + ts_usec / 1e6
                size = row[3]

                if last_time is not None:
                    delta_time = time - last_time
                    bandwidth = (size / delta_time) / 1e6
                    times.append(time)
                    sizes.append(bandwidth)
                    if bandwidth < 0:
                        print("?????")

                last_time = time

            print("bandwidth=", sizes)
            ax.plot(times, sizes, color=trace_plot.plot_color, label=f'Trace {trace_plot.trace_id}')

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Bandwidth (Mb/s)')
        ax.legend()
        plt.savefig("out/bandwidth")
        # plt.show()

    @staticmethod
    def plot_wavelet_multiresolution_energy_analysis_pps(trace_plots):
        fig, ax = plt.subplots()
        wavelet = 'db4'
        for trace_plot in trace_plots:
            packets = trace_plot.fetch_packets()
            timestamps = np.array([row[0] + row[1]/1e6 for row in packets])
            packet_counts = np.array([row[2] for row in packets])
            energy = pywt.swt(packet_counts, wavelet)
            ax.plot(timestamps, energy[0], color=trace_plot.plot_color, label=f'Trace {trace_plot.trace_id}')

        ax.set_xlabel('Timestamp (s)')
        ax.set_ylabel('Energy')
        ax.set_title('Wavelet Multiresolution Energy Analysis of Packet Counts')
        ax.legend(loc='upper right')
        plt.show()

