import matplotlib.pyplot as plt
import pywt
import sqlite3
import numpy as np
import os
import pywt
from Utils import Utils


class Plotter:

    @staticmethod
    def plot_inter_arrival_cdf(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:
            print(f"Plotting element {item.name}...")
            data = item.load(["inter-arrival-times"])
            inter_arrival_times = data["inter-arrival-times"]
            # sort the inter arrival times
            sorted_inter_arrival_times = np.sort(inter_arrival_times)
            # calculate the empirical CDF
            ecdf = np.arange(1, len(sorted_inter_arrival_times) + 1) / len(sorted_inter_arrival_times)
            # plot the CDF
            plt.plot(sorted_inter_arrival_times, ecdf, label=item.name, color=item.color)

        plt.legend()
        plt.grid(True)
        plt.title('Empirical CDF of Inter-Arrival Times')
        plt.xlabel('Inter-Arrival Time (seconds)')
        plt.ylabel('Cumulative Probability')
        plot_file = os.path.join(out_dir, f"InterArrivalCDF_{nickname}.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_inter_arrival_time_distribution(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:
            data = item.load(["inter-arrival-times"])
            inter_arrival_times = data["inter-arrival-times"]
            print(f"Plotting element {item.name}...")
            # Calculate the histogram
            hist, edges = np.histogram(inter_arrival_times, bins='auto')
            # Plot the histogram as a curve
            plt.plot(edges[:-1], hist, color=item.color, label=item.name)

        plt.legend()
        plt.grid(True)
        plt.title('Inter-Arrival Time Distribution')
        plt.xlabel('Inter-Arrival Time (seconds)')
        plt.ylabel('Frequency')
        plot_file = os.path.join(out_dir, f"InterArrivalTimeDistribution{nickname}.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_bandwidth_mbps(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:
            print(f"Plotting element {item.name}...")

            data = item.load(["inter-arrival-times", "pktSize"])

            inter_arrival_times = data["inter-arrival-times"]
            packet_sizes = data["pktSize"]

            time_slices, bandwidth = Utils.calc_bandwidth(inter_arrival_times,
                                                          packet_sizes,
                                                          time_resolution=1.0,
                                                          verbose=False)
            plt.plot(time_slices, bandwidth/1e6, label=item.name, color=item.color)

        plt.legend()
        plt.grid(True)
        title = 'Bandwidth over Time'
        plt.title(title)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Bandwidth (MBytes per second)')
        plot_file = os.path.join(out_dir, f"BandwidthMbps_{nickname}.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_pps(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:
            print(f"Plotting element {item.name}...")

            data = item.load(["inter-arrival-times"])

            inter_arrival_times = data["inter-arrival-times"]

            time_slices, pps = Utils.calc_pps(inter_arrival_times,
                                              time_resolution=1.0,
                                              verbose=False)
            plt.plot(time_slices, pps, label=item.name, color=item.color)

        plt.legend()
        plt.grid(True)
        title = 'Packet Per Second'
        plt.title(title)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Packet Per Second')
        plot_file = os.path.join(out_dir, f"Pps_{nickname}.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_wavelet_multiresolution_energy(plot_data_list, out_dir, number_of_scales=15, nickname=""):
        print("Practical Introduction to Multiresolution Analysis: ",
              "https://www.mathworks.com/help/wavelet/ug/practical-introduction-to-multiresolution-analysis.html")
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:

            # load the data
            data = item.load(["arrival-times", "pktSize"])

            arrival_times = data["arrival-times"]
            packet_sizes = data["pktSize"]

            # execute wavelet analysis
            scales, energy_values = Utils.wavelet_multiresolution_energy_analysis_xy(arrival_times=arrival_times,
                                                                                     packet_sizes=packet_sizes,
                                                                                     number_of_scales=number_of_scales)

            # plot data
            plt.plot(scales, energy_values, marker='o', label=item.name, color=item.color)

        plt.legend()
        plt.grid(True)
        plt.xlabel('j = log2(time_scale) + 1, time_scale (ms)')
        plt.ylabel('log2(Energy(j))')
        plt.title('Wavelet Multiresolution Energy Analysis')
        plot_file = os.path.join(out_dir, f"WaveletMultiresolutionEnergyAnalysis_{nickname}.png")
        plt.savefig(plot_file)


    @staticmethod
    def plot_flow_cdf(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:

            data = item.load(["arrival-times", "flowID"])

            arrival_times = data["arrival-times"]
            flow_ids = data["flowID"]

            #  returns an array with the same size but with the greatest value so far for each position.
            #  out[i] = max(in[i], in(i-1), ..., in(0))
            cumulative_flows = np.maximum.accumulate(flow_ids)

            plt.plot(arrival_times, cumulative_flows, label=item.name, color=item.color)

        plt.legend()
        plt.grid(True)
        plt.xlabel("Time")
        plt.ylabel("Cumulative Flow Count")
        plt.title("Flow Cumulative Distribution")
        plot_file = os.path.join(out_dir, f"FlowCumulativeDistribution_{nickname}.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_bytes_cdf(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        plt.clf()

        for item in plot_data_list:

            data = item.load(["arrival-times", "pktSize"])

            arrival_times = data["arrival-times"]
            pkt_sizes = data["pktSize"]

            # accumulate the packet sizes
            #  out[i] = in[i] + in(i-1) +  ... + in(0))
            accumulated_pkt_sizes = np.maximum.accumulate(pkt_sizes)

            plt.plot(arrival_times, accumulated_pkt_sizes, label=item.name, color=item.color)

        plt.legend()
        plt.grid(True)
        plt.xlabel("Time")
        plt.ylabel("Cumulative Bytes Count")
        plt.title("Bytes Cumulative Distribution")
        plot_file = os.path.join(out_dir, f"BytesCumulativeDistribution_{nickname}.png")
        plt.savefig(plot_file)

    @staticmethod
    def plot_wavelet_power_spectrum(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        plt.clf()
        plt.figure(figsize=(10, 6))

        wavelet = 'morl'
        for item in plot_data_list:
            data = item.load(["arrival-times", "pktSize"])

            arrival_times = data["arrival-times"]
            pkt_sizes = data["pktSize"]

            coeffs, freqs = pywt.cwt(pkt_sizes, np.arange(1, len(pkt_sizes) + 1), wavelet)
            power = (np.abs(coeffs) ** 2) / np.mean(np.abs(coeffs) ** 2)

            time_grid, freq_grid = np.meshgrid(arrival_times, freqs)

            plt.ylim(freqs[0], freqs[-1])
            plt.gca().set_aspect('auto')
            plt.pcolormesh(time_grid, freq_grid, power, shading='auto', cmap='jet', alpha=0.7, label=item.name)

        plt.legend()
        # plt.grid(True)
        plt.colorbar(label='Power')
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.title('Wavelet Power Spectrum')
        plot_file = os.path.join(out_dir, f"WaveletPowerSpectrum_{nickname}.png")
        plt.savefig(plot_file)

