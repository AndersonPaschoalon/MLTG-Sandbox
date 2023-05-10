import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from scipy import signal
import pywt
import random
# import hurst
import Hurst


def sample_inter_arrival_times_ms(sample, repeat=1):
    if sample == 1:
        s = [16.4322, 20.4638, 31.4781, 13.7591, 26.3582, 18.1446, 19.5477, 16.1248, 22.6149, 23.3728, 12.6787, 23.2011, 15.0972, 24.7529, 26.1879, 23.9084, 22.1554, 23.3728, 13.2734, 22.7696, 15.7415, 20.0801, 16.4322, 20.5544, 17.2459, 21.3111, 17.8427, 16.8386, 17.6482, 16.8386, 21.7047, 19.5477, 20.7675, 22.4205, 14.9677, 19.358, 23.102, 15.4457, 17.8427, 21.7047, 16.1248, 15.9311, 18.3427, 22.6149, 15.9311, 21.3111, 18.5537, 17.2459, 17.2459, 14.173, 14.9677, 25.1439, 22.6149, 21.7047, 18.5537, 17.6482, 24.7529, 20.5544, 18.5537, 21.1088, 18.1446, 21.3111, 19.1544, 22.1554, 21.7047, 20.0801, 17.2459, 19.5477, 22.7696, 20.0801, 18.5537, 16.638, 18.7504, 20.0801, 19.358, 15.7415, 18.1446, 14.5687, 21.7047, 21.3111, 16.638, 17.8427, 23.9084, 15.9311, 18.3427, 18.1446, 18.3427, 21.1088, 20.0801, 22.4205, 19.7473, 20.0801, 17.2459, 22.4205, 21.7047, 21.1088, 22.6149, 16.638, 23.102, 20.5544, 19.7473]
        if repeat > 1:
            s = list(s * repeat)
        return s
    else :
        return [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1, 1.125, 1.25, 1.375, 1.5, 1.625, 1.75, 1.875, 2, 2.125, 2.25, 2.375, 2.5, 2.625, 2.75, 2.875, 3, 3.125, 3.25, 3.375, 3.5, 3.625, 3.75, 3.875, 4, 4.125, 4.25, 4.375, 4.5, 4.625, 4.75, 4.875, 5, 5.125, 5.25, 5.375, 5.5, 5.625, 5.75, 5.875, 6, 6.125, 6.25, 6.375, 6.5, 6.625, 6.75, 6.875, 7, 7.125, 7.25, 7.375, 7.5, 7.625, 7.75, 7.875, 8, 8.125, 8.25, 8.375, 8.5, 8.625, 8.75, 8.875, 9, 9.125, 9.25, 9.375, 9.5, 9.625, 9.75, 9.875, 10, 10.125, 10.25, 10.375, 10.5, 10.625, 10.75, 10.875, 11, 11.125, 11.25, 11.375, 11.5, 11.625, 11.75, 11.875]


def _generate_weibull_interarrival(n, shape, scale):
    interarrival = np.random.weibull(shape, size=n)
    interarrival = interarrival * scale
    return interarrival


def _generate_integers(n, min_val, max_val):
    return [random.randint(min_val, max_val) for _ in range(n)]


def sample_flows(n_packets, n_flows):
    return _generate_integers(n_packets, 1, n_flows)


def sample_inter_arrival_times_ms_weibull(sample_size=100):
    shape = 1.5
    scale = 7.5
    return _generate_weibull_interarrival(sample_size, shape, scale)


def samplepacket_sizes(n):
    # Ethernet packet size range (64-1518 bytes)
    min_size = 64
    max_size = 1518
    # Generate `n` packet sizes uniformly at random within the range
    return np.random.randint(min_size, max_size + 1, size=n).tolist()


def plot_interarrival_histogram(interarrival_times, sample_nickname):
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
    plt.savefig("InterarrivalTimeDistribution" + sample_nickname)


def plot_interarrival_cdf(interarrival_times, sample_nickname):
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
    plt.savefig( "InterarrivalCDF" + sample_nickname)
    plt.clf()


def plot_acf_interarrival_times(interarrival_times, sample_nickname):
    plt.clf()
    fig, ax = plt.subplots(figsize=(10, 5))
    plot_acf(interarrival_times, lags=len(interarrival_times)-1, ax=ax)
    ax.set_xlabel("Lag")
    ax.set_ylabel("ACF")
    ax.set_title("Autocorrelation Function of Interarrival Times")
    plt.savefig("AutocorrelationFunctionofInterarrivalTimes" + sample_nickname)


def plot_psd(interarrival_times, sample_nickname):
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
    plt.savefig("PowerSpectralDensity" + sample_nickname)


def plot_time_series(interarrival_times, sample_nickname):
    # Compute the cumulative sum of interarrival times
    cumsum = np.cumsum(interarrival_times)

    # Plot the time series
    plt.clf()
    plt.plot(cumsum)
    plt.xlabel('Packet Index')
    plt.ylabel('Cumulative Sum of Interarrival Times (ms)')
    plt.title('Time Series Plot')
    plt.savefig("TimeSeriesPlot" + sample_nickname)


# wavelet
# conda install -c conda-forge pywavelets
# This will produce a plot showing the wavelet multiresolution energy analysis of the interarrival times.
# The x-axis represents the frequency scale (Hz) and the y-axis represents the percentage of total energy at
# each scale. This type of analysis can be useful for identifying frequency patterns and trends in the interarrival
# times.
def wavelet_energy_plot(interarrival_times, sample_nickname):
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
    plt.savefig("WaveletMultiresolutionEnergyAnalysis" + sample_nickname)


def plot_bandwidth2(interarrival_times, packet_sizes, sample_nickname):
    title = 'Bandwidth over Time'
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

    # Plot the bandwidth over time
    plt.clf()
    plt.plot(np.arange(len(bandwidth)), bandwidth)
    plt.title(title)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Bandwidth (mbytes per second)')
    plt.savefig("Bandwidth" + sample_nickname)


def plot_bandwidth(interarrival_times, packet_sizes, sample_nickname):
    time = [0]
    bandwidth = [0]

    for i in range(1, len(interarrival_times)):
        delta_time = interarrival_times[i] - interarrival_times[i-1]
        time.append(interarrival_times[i])
        bandwidth.append(packet_sizes[i] / delta_time)
    plt.clf()
    plt.plot(time, bandwidth)
    plt.xlabel('Time (s)')
    plt.ylabel('Bandwidth (bytes/s)')
    plt.savefig("Bandwidth" + sample_nickname)


def plot_flow_per_second(packet_flow, packet_interarrival_times, sample_nickname):
    # Calculate the start and end times for each packet
    start_times = np.cumsum(packet_interarrival_times) - packet_interarrival_times
    end_times = np.cumsum(packet_interarrival_times)

    # Determine the time range covered by the packets
    total_time = end_times[-1] - start_times[0]
    num_bins = int(total_time * 1000) + 1  # bins in milliseconds

    # Create a histogram of flow counts over time
    hist, bins = np.histogram(start_times, bins=num_bins, weights=np.ones_like(packet_flow))

    # Convert histogram to flow per second
    flow_per_second = hist * 1000 / np.diff(bins)

    # Plot the results
    fig, ax = plt.subplots()
    ax.plot(bins[:-1], flow_per_second)
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Number of flows per second')
    ax.set_title('Flow rate over time')
    plt.savefig('flow_per_second' + sample_nickname)



def plot_local_hurst(ts, window_size=50, sample_nickname=""):
    """
    Plots the local Hurst exponent of a time series.

    Args:
        ts (numpy.ndarray): The time series.
        window_size (int): The size of the window used for local Hurst exponent calculation.

    Returns:
        None.
    """

    # Calculate the cumulative sum and deviation of the time series
    cum_sum = np.cumsum(ts - np.mean(ts))
    cum_dev = cum_sum - np.arange(1, len(ts) + 1) * np.mean(ts)

    # Initialize arrays for scaling factors and fluctuation values
    scales = np.arange(1, window_size)
    flucts = np.zeros_like(scales)

    # Iterate over the window sizes
    for i, sc in enumerate(scales):
        # Determine the number of windows
        num_windows = np.floor(len(ts) / sc).astype(int)

        # Initialize arrays for local variances
        local_ranges = np.zeros(num_windows)
        local_vars = np.zeros(num_windows)

        # Iterate over the windows
        for j in range(num_windows):
            start = j * sc
            end = start + sc

            # Calculate the local range and variance
            local_ranges[j] = np.max(cum_sum[start:end]) - np.min(cum_sum[start:end])
            local_vars[j] = np.var(ts[start:end])

        # Calculate the local fluctuation
        flucts[i] = np.sqrt(np.mean(local_ranges ** 2)) / np.mean(np.sqrt(local_vars))

    # Calculate the local Hurst exponent
    hurst = np.log(flucts) / np.log(scales)

    # Plot the local Hurst exponent
    plt.plot(hurst)
    plt.xlabel('Window size (log scale)')
    plt.ylabel('Hurst exponent')
    plt.xscale('log')
    plt.savefig('localHurstExponent' + sample_nickname)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    n_samples = 10000
    n_flows = 150
    # vec_samples = sample_inter_arrival_times_ms(n_samples)
    # vec_samples = sample_inter_arrival_times_ms_weibull(n_samples)
    # vec_pkt_sizes = samplepacket_sizes(n_samples)
    # vec_flows = sample_flows(n_samples, n_flows)

    # plot_interarrival_histogram(vec_samples, "weibull_samples")
    # plot_interarrival_cdf(vec_samples, "weibull_samples")
    # plot_acf_interarrival_times(vec_samples, "weibull_samples")
    # plot_psd(vec_samples, "weibull_samples")
    # plot_bandwidth2(vec_samples, vec_pkt_sizes, "weibull_samples")
    # plot_bandwidth(vec_samples, vec_pkt_sizes, "weibull_samples")
    # wavelet_energy_plot(vec_samples, "weibull_samples")
    # plot_flow_per_second(vec_flows, vec_samples, "weibull_samples")
    # plot_local_hurst(vec_samples, window_size=50, sample_nickname="weibull_samples")
    ts = list(range(50))
    h, c, log_R_S, log_n = Hurst.hurst(ts)
    print(f"h:{h}, c:{c}, log_R_S:{log_R_S}, log_n:{log_n}")




