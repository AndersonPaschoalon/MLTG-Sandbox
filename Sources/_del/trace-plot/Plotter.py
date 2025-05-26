import matplotlib.pyplot as plt
import pywt
import sqlite3
from statsmodels.graphics.tsaplots import plot_acf
from scipy import signal
import numpy as np
import os
import pywt
from Utils import Utils
from hurst import compute_Hc, random_walk

class Plotter:

    @staticmethod
    def plot_all_stable(plot_data_list, out_dir, nickname="default"):
        Plotter.plot_inter_arrival_cdf(plot_data_list=plot_data_list, out_dir=out_dir, nickname=nickname)
        Plotter.plot_inter_arrival_time_distribution(plot_data_list=plot_data_list, out_dir=out_dir, nickname=nickname)
        Plotter.plot_bytes_cdf(plot_data_list=plot_data_list, out_dir=out_dir, nickname=nickname)
        Plotter.plot_flow_cdf(plot_data_list=plot_data_list, out_dir=out_dir, nickname=nickname)
        Plotter.plot_bandwidth_mbps(plot_data_list=plot_data_list, out_dir=out_dir, nickname=nickname)
        Plotter.plot_wavelet_power_spectrum(plot_data_list=plot_data_list, out_dir=out_dir, nickname=nickname)
        Plotter.plot_spectrum(plot_data_list=plot_data_list, out_dir=out_dir, nickname=nickname)
        Plotter.plot_power_spectrum_density(plot_data_list=plot_data_list, out_dir=out_dir, nickname=nickname)
        Plotter.plot_wavelet_multiresolution_energy(plot_data_list=plot_data_list,
                                                    out_dir=out_dir,
                                                    nickname=nickname)
        Plotter.plot_acf_bandwidth(plot_data_list=plot_data_list, out_dir=out_dir, nickname=nickname)
        # Plotter.plot_hurst_rs(plot_data_list=plot_data_list, out_dir=out_dir, nickname="weibull")

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
        for item in plot_data_list:
            plt.clf()
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
            title = f'Bandwidth over Time of {item.name}'
            plt.title(title)
            plt.xlabel('Time (seconds)')
            plt.ylabel('Bandwidth (MBytes per second)')
            plot_file = os.path.join(out_dir, f"BandwidthMbps_{item.name}_{nickname}.png")
            plt.savefig(plot_file)

    @staticmethod
    def plot_pps(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        for item in plot_data_list:
            plt.clf()

            print(f"Plotting element {item.name}...")
            data = item.load(["inter-arrival-times"])
            inter_arrival_times = data["inter-arrival-times"]

            time_slices, pps = Utils.calc_pps(inter_arrival_times,
                                              time_resolution=1.0,
                                              verbose=False)
            plt.plot(time_slices, pps, label=item.name, color=item.color)

            plt.legend()
            plt.grid(True)
            title = f'Packet Per Second of of {item.name}'
            plt.title(title)
            plt.xlabel('Time (seconds)')
            plt.ylabel('Packet Per Second')
            plot_file = os.path.join(out_dir, f"Pps_{item.name}_{nickname}.png")
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
                                                                                     number_of_scales=number_of_scales,
                                                                                     wavelet='haar')

            # plot data
            plt.plot(scales, energy_values, marker='o', label=item.name, color=item.color)

        plt.legend()
        plt.grid(True)
        plt.xlabel('j = log2(time_scale) + 1, time_scale (ms)')
        plt.ylabel('log2(Energy(j))')
        plt.title('Bandwidth Wavelet Multiresolution Energy Analysis')
        plot_file = os.path.join(out_dir, f"BandwidthWaveletMultiresolutionEnergyAnalysis_{nickname}.png")
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
            cumulative_flows = cumulative_flows / np.max(cumulative_flows)

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
            accumulated_pkt_sizes = accumulated_pkt_sizes / np.max(accumulated_pkt_sizes)

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

        for item in plot_data_list:

            # clean the plot
            plt.clf()

            # load the data
            data = item.load(["inter-arrival-times", "pktSize"])

            inter_arrival_times = data["inter-arrival-times"]
            pkt_sizes = data["pktSize"]
            instant_bw = Utils.calc_instant_bw(inter_arrival_times, pkt_sizes)

            # Define the  wavelet
            wavelet = 'morl'
            # wavelet = 'mexh'

            # Define the scales to be used in the wavelet transform
            scales = np.arange(1, len(instant_bw) + 1)

            # convert to better scales
            scales = scales.astype(np.float16)
            instant_bw = instant_bw.astype(np.float16)

            # Perform the wavelet transform
            coeffs, freqs = pywt.cwt(instant_bw, scales, wavelet)

            # Calculate the power spectrum
            power = (abs(coeffs)) ** 2

            # Plot the power spectrum
            plt.imshow(power, cmap='jet', extent=[0, len(instant_bw), freqs[-1], freqs[0]],
                       aspect='auto', interpolation='nearest')
            plt.colorbar()
            plt.title(f'Wavelet Power Spectrum of of {item.name}')
            plt.xlabel('Time')
            plt.ylabel('Frequency')

            plot_file = os.path.join(out_dir, f"WaveletPowerSpectrum_{item.name}_{nickname}.png")
            plt.savefig(plot_file)

    @staticmethod
    def plot_spectrum(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        plt.clf()

        # sampling rate
        # fs = 0.5*1e-6
        fs = 1000

        for item in plot_data_list:
            plt.clf()

            data = item.load(["inter-arrival-times", "pktSize"])

            inter_arrival_times = data["inter-arrival-times"]
            pkt_sizes = data["pktSize"]

            # _, bandwidth = Utils.calc_bandwidth(inter_arrival_times, pkt_sizes, time_resolution=1e-3)
            _, bandwidth = Utils.calc_bandwidth(inter_arrival_times, pkt_sizes, time_resolution=1)

            # plotting the magnitude spectrum of the signal
            plt.magnitude_spectrum(bandwidth, color=item.color)

            plt.title("Magnitude Spectrum of the Bandwidth Signal")
            plt.xlabel('Frequency')
            plt.ylabel('Energy')

            plot_file = os.path.join(out_dir, f"Spectrum_{item.name}_{nickname}.png")
            plt.savefig(plot_file)

    @staticmethod
    def plot_power_spectrum_density(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        fs = 1000.0  # Sampling frequency (1 kHz)
        for item in plot_data_list:
            plt.clf()

            data = item.load(["inter-arrival-times", "pktSize"])

            inter_arrival_times = data["inter-arrival-times"]
            pkt_sizes = data["pktSize"]

            # _, bandwidth = Utils.calc_bandwidth(inter_arrival_times, pkt_sizes, time_resolution=1e-3)
            _, bandwidth = Utils.calc_bandwidth(inter_arrival_times, pkt_sizes, time_resolution=1)

            f, psd = signal.welch(inter_arrival_times, fs, nperseg=len(inter_arrival_times))

            plt.clf()
            plt.figure(figsize=(8, 4))
            plt.semilogy(f, psd)
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('PSD')
            plt.title(f'Power Spectral Density of {item.name}')

            plot_file = os.path.join(out_dir, f"PoweSpectrumDensity_{item.name}_{nickname}.png")
            plt.savefig(plot_file)

    @staticmethod
    def plot_acf_bandwidth(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        for item in plot_data_list:
            plt.clf()

            data = item.load(["inter-arrival-times", "pktSize"])
            inter_arrival_times = data["inter-arrival-times"]
            pkt_sizes = data["pktSize"]
            _, bandwidth = Utils.calc_bandwidth(inter_arrival_times, pkt_sizes, time_resolution=1)

            fig, ax = plt.subplots(figsize=(10, 5))
            plot_acf(bandwidth, lags=len(bandwidth)-1, ax=ax)
            ax.set_xlabel("Lag")
            ax.set_ylabel("ACF")
            ax.set_title(f"Autocorrelation Function of Bandwidth of {item.name}")

            plot_file = os.path.join(out_dir, f"AutocorrelationFunctionofBandwidth_{nickname}_{item.name}.png")
            plt.savefig(plot_file)

    @staticmethod
    def plot_hurst_rs(plot_data_list, out_dir, nickname=""):
        Utils.mkdir(out_dir)
        for item in plot_data_list:
            plt.clf()

            data = item.load(["inter-arrival-times", "pktSize"])
            inter_arrival_times = data["inter-arrival-times"]
            pkt_sizes = data["pktSize"]
            _, bandwidth = Utils.calc_bandwidth(inter_arrival_times, pkt_sizes, time_resolution=1e-2)
            H, c, array_r_s, array_n = Utils.hurst(bandwidth)

            # Plot
            f, ax = plt.subplots()
            # ax.scatter(log_n, log_r_s, color="purple")
            #ax.plot(log_n[0], c * log_n[0] ** H, color="deepskyblue")
            #ax.plot(log_n, c * log_n ** H, color="deepskyblue")
            ax.plot(array_n, c * array_n ** H, color="deepskyblue")
            ax.scatter(array_n, array_r_s, color="purple")
            # ax.set_xscale('log')
            # ax.set_yscale('log')
            ax.set_xlabel('ln(Time) interval')
            ax.set_ylabel('ln(R/S) ratio')
            ax.grid(True)
            title_str = "H={:.4f}, c={:.4f}".format(H, c) + f" of {item.name}"
            plt.title(title_str)

            plot_file = os.path.join(out_dir, f"HurstRS_{nickname}_{item.name}.png")
            plt.savefig(plot_file)


