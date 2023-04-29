import matplotlib.pyplot as plt
import pywt
import sqlite3
import numpy as np
from Utils import Utils
import os
import math
from scipy import signal
import pywt

class Plotter:

    @staticmethod
    def plot_interarrival_cdf(plot_data_list, out_dir, nickname=""):
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
        plt.xlabel('Interarrival Time (seconds)')
        plt.ylabel('Cumulative Probability')
        plt.legend()
        plot_file = os.path.join(out_dir, f"InterarrivalCDF{nickname}.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_interarrival_time_distribution(plot_data_list, out_dir, nickname=""):
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
        plt.xlabel('Interarrival Time (seconds)')
        plt.ylabel('Frequency')
        plot_file = os.path.join(out_dir, f"InterarrivalTimeDistribution{nickname}.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_bandwidth_mbps(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:
            print(f"Plotting element {item.name}...")
            interarrival_times = item.inter_arrivals()
            packet_sizes = item.packet_sizes()
            time_slices, bandwidth = Utils.calc_bandwidth(interarrival_times,
                                                          packet_sizes,
                                                          time_resolution=1.0,
                                                          verbose=False)
            plt.plot(time_slices, bandwidth/1e6, label=item.name, color=item.color)

        plt.legend()
        title = 'Bandwidth over Time'
        plt.title(title)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Bandwidth (MBytes per second)')
        plot_file = os.path.join(out_dir, f"BandwidthMbps{nickname}.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_wavelet_multiresolution_energy(plot_data_list, out_dir, number_of_scales=15):
        print("Practical Introduction to Multiresolution Analysis: ",
              "https://www.mathworks.com/help/wavelet/ug/practical-introduction-to-multiresolution-analysis.html")
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:
            # load the data
            arrival_times, packet_sizes = item.arrival_times_and_pkt_sizes()

            # execute wavelet analysis
            scales, energy_values = Utils.wavelet_multiresolution_energy_analysis_xy(arrival_times=arrival_times,
                                                                                     packet_sizes=packet_sizes,
                                                                                     number_of_scales=number_of_scales)

            # plot data
            plt.plot(scales, energy_values, marker='o', label=item.name, color=item.color)

        plt.xlabel('j = log2(time_scale) + 1, time_scale (ms)')
        plt.ylabel('log2(Energy(j))')
        plt.title('Wavelet Multiresolution Energy Analysis')
        plt.grid(True)
        plot_file = os.path.join(out_dir, "WaveletMultiresolutionEnergyAnalysis.png")
        plt.savefig(plot_file)

    @staticmethod
    def _calc_wavelet_xy(bandwidth_data):
        num_scales = len(bandwidth_data)

        energy_values = []
        for j in range(1, num_scales + 1):
            # Perform wavelet transform
            coeffs = pywt.wavedec(bandwidth_data[j - 1], 'db4', level=num_scales)
            cA = coeffs[0]
            # Calculate energy
            energy = np.sum(np.square(cA))
            energy_values.append(np.log2(energy))

        scales = np.arange(1, num_scales + 1)

        return scales, energy_values