import matplotlib.pyplot as plt
import pywt
import sqlite3
import numpy as np
import os
from statsmodels.graphics.tsaplots import plot_acf
from scipy import signal
import pywt
import random
import hurst


class Plotter:

    def __init__(self, out_dir):
        self.out_dir = out_dir

    def plot_interarrival_cdf(self, interarrival_times, sample_nickname):
        # sort the interarrival times
        sorted_interarrival_times = np.sort(interarrival_times)

        # calculate the empirical CDF
        ecdf = np.arange(1, len(sorted_interarrival_times) + 1) / len(sorted_interarrival_times)

        # plot the CDF
        plt.clf()
        plt.plot(sorted_interarrival_times, ecdf)

        # set the plot title and axis labels
        plt.title('Empirical CDF of Interarrival Times')
        plt.xlabel('Interarrival Time (ms)')
        plt.ylabel('Cumulative Probability')

        # show the plot
        file = os.path.join(self.out_dir, "InterarrivalCDF_" + sample_nickname)
        plt.savefig(file)
        plt.clf()


    def plot_interarrival_histogram(self, interarrival_times, sample_nickname):
        """
        Plots a histogram of the distribution of interarrival times.

        Parameters:
            interarrival_times (list of floats): List of interarrival times in milliseconds.
            filename (str): Name of the file to save the figure to.
        """
        plt.hist(interarrival_times, bins='auto')
        plt.title('Interarrival Time Distribution')
        plt.xlabel('Interarrival Time (ms)')
        plt.ylabel('Frequency')
        file = os.path.join(self.out_dir, "InterarrivalTimeDistribution" + sample_nickname)
        plt.savefig(file)
        plt.clf()


    def plot_interarrival_cdf(self, interarrival_times, sample_nickname):
        # sort the interarrival times
        sorted_interarrival_times = np.sort(interarrival_times)

        # calculate the empirical CDF
        ecdf = np.arange(1, len(sorted_interarrival_times) + 1) / len(sorted_interarrival_times)

        # plot the CDF
        plt.clf()
        plt.plot(sorted_interarrival_times, ecdf)

        # set the plot title and axis labels
        plt.title('Empirical CDF of Interarrival Times')
        plt.xlabel('Interarrival Time (ms)')
        plt.ylabel('Cumulative Probability')

        # show the plot
        file = os.path.join(self.out_dir, "InterarrivalCDF" + sample_nickname)
        plt.savefig(file)
        plt.clf()


    def plot_acf_interarrival_times(self, interarrival_times, sample_nickname):
        plt.clf()
        fig, ax = plt.subplots(figsize=(10, 5))
        plot_acf(interarrival_times, lags=len(interarrival_times)-1, ax=ax)
        ax.set_xlabel("Lag")
        ax.set_ylabel("ACF")
        ax.set_title("Autocorrelation Function of Interarrival Times")

        file = os.path.join(self.out_dir, "AutocorrelationFunctionofInterarrivalTimes" + sample_nickname)
        plt.savefig(file)
        plt.clf()


    def plot_psd(self, interarrival_times, sample_nickname):
        # Compute power spectral density
        fs = 1000.0  # Sampling frequency (1 kHz)
        f, psd = signal.welch(interarrival_times, fs, nperseg=len(interarrival_times))
        # Plot PSD
        plt.clf()
        plt.figure(figsize=(8, 4))
        plt.semilogy(f, psd)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('PSD')
        plt.title('Power Spectral Density')

        file = os.path.join(self.out_dir, "PowerSpectralDensity" + sample_nickname)
        plt.savefig(file)
        plt.clf()


    def plot_time_series(self, interarrival_times, sample_nickname):
        # Compute the cumulative sum of interarrival times
        cumsum = np.cumsum(interarrival_times)

        # Plot the time series
        plt.clf()
        plt.plot(cumsum)
        plt.xlabel('Packet Index')
        plt.ylabel('Cumulative Sum of Interarrival Times (ms)')
        plt.title('Time Series Plot')

        file = os.path.join(self.out_dir, "TimeSeriesPlot" + sample_nickname)
        plt.savefig(file)
        plt.clf()


    # wavelet
    # conda install -c conda-forge pywavelets
    # This will produce a plot showing the wavelet multiresolution energy analysis of the interarrival times.
    # The x-axis represents the frequency scale (Hz) and the y-axis represents the percentage of total energy at
    # each scale. This type of analysis can be useful for identifying frequency patterns and trends in the interarrival
    # times.
    def wavelet_energy_plot(self, interarrival_times, sample_nickname):
        # Define wavelet family and level of decomposition
        wavelet = 'db4'
        # level = 6
        # level = 5
        level = 6

        # Decompose interarrival_times using wavelet transform
        coeffs = pywt.wavedec(interarrival_times, wavelet, level=level)

        # Calculate energy at each level
        energies = []
        for i in range(level+1):
            energy = np.sum(coeffs[i]**2)
            energies.append(energy)

        # Calculate percentage of total energy at each level
        total_energy = np.sum(energies)
        energy_percentages = [energy/total_energy*100 for energy in energies]

        # Plot energy percentages vs. scale (level)
        plt.clf()
        scales = pywt.scale2frequency(wavelet, np.arange(level+1))
        fig, ax = plt.subplots()
        ax.plot(scales, energy_percentages, marker='o')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Energy (%)')
        ax.set_title('Wavelet Multiresolution Energy Analysis')
        ax.grid(True)

        file = os.path.join(self.out_dir, "WaveletMultiresolutionEnergyAnalysis" + sample_nickname)
        plt.savefig(file)
        plt.clf()
