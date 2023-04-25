import matplotlib.pyplot as plt
import pywt
import sqlite3
import numpy as np
from Utils import Utils
import os


class Plotter:

    @staticmethod
    def plot_interarrival_cdf(plot_data_list, out_dir):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:
            print(f"Plotting element {item.name}...")
            interarrival_times = item.inter_arrivals()

            # sort the interarrival times
            sorted_interarrival_times = np.sort(interarrival_times)

            # calculate the empirical CDF
            ecdf = np.arange(1, len(sorted_interarrival_times) + 1) / len(sorted_interarrival_times)

            # plot the CDF
            plt.plot(sorted_interarrival_times, ecdf, label=item.name, color=item.color)

        plt.title('Empirical CDF of Interarrival Times')
        plt.xlabel('Interarrival Time (ms)')
        plt.ylabel('Cumulative Probability')
        plt.legend()
        plot_file = os.path.join(out_dir, "InterarrivalCDF.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_interarrival_time_distribution(plot_data_list, out_dir):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:
            data = item.inter_arrivals()
            print(f"Plotting element {item.name}...")
            # Calculate the histogram
            hist, edges = np.histogram(data, bins='auto')
            # Plot the histogram as a curve
            plt.plot(edges[:-1], hist, color=item.color, label=item.name)

        plt.legend()
        plt.title('Interarrival Time Distribution')
        plt.xlabel('Interarrival Time (ms)')
        plt.ylabel('Frequency')
        plot_file = os.path.join(out_dir, "InterarrivalTimeDistribution.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_iplot_bandwidth_mbps(plot_data_list, out_dir):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:
            print(f"Plotting element {item.name}...")
            interarrival_times = item.inter_arrivals()
            packet_sizes = item.packet_sizes()

            # Calculate the start times for each packet
            start_times = np.cumsum(interarrival_times)

            # Calculate the number of seconds elapsed for each packet
            elapsed_seconds = start_times - start_times[0]
            elapsed_seconds = elapsed_seconds // 1000

            # Calculate the total amount of data transmitted in each second
            data_per_second = np.zeros(elapsed_seconds[-1] + 1)
            for i in range(len(packet_sizes)):
                data_per_second[elapsed_seconds[i]] += packet_sizes[i]

            # Calculate the bandwidth in mbytes per second
            bandwidth = data_per_second / 1e6 / np.diff(np.concatenate(([0], elapsed_seconds)))

            plt.plot(np.arange(len(bandwidth)), bandwidth, label=item.name, color=item.color)


        plt.legend()
        title = 'Bandwidth over Time'
        plt.title(title)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Bandwidth (MBytes per second)')
        plot_file = os.path.join(out_dir, "BandwidthMbps.png")
        plt.savefig(plot_file)

"""
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
"""
