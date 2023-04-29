import numpy as np
import math


def _calc_bandwidth(interarrival_times, packet_sizes, time_resolution=1.0, verbose=False):
    total_time = np.sum(interarrival_times)
    num_slices = math.ceil(total_time / time_resolution)

    time_slices = np.arange(time_resolution, total_time + time_resolution, time_resolution)
    pkt_size_acc = np.zeros(num_slices)

    curr_slice = 0
    curr_time = 0
    curr_sum = 0

    for i in range(len(interarrival_times)):
        curr_time += interarrival_times[i]
        if curr_time > time_slices[curr_slice]:
            # if the current time does not belong to the current time slice
            # search for the next time slice with packets available
            while curr_time > time_slices[curr_slice]:
                curr_slice += 1
                if curr_slice >= num_slices:
                    break
        # accumulate the packet size in the current time slice array
        pkt_size_acc[curr_slice] += packet_sizes[i]

    # calc the bandwidth
    bandwidth = pkt_size_acc / time_resolution
    if verbose:
        print("Time Slices:", time_slices)
        print("Bandwidth:", bandwidth)
    return time_slices, bandwidth



def gen_interarrival_and_pkt_sizes():
    np.random.seed(42)

    # Parameters
    total_time = 60  # Total duration in seconds
    num_packets = 30  # Total number of packets

    # Generate interarrival times with spikes
    interarrival_times1 = []
    interarrival_times2 = []
    interarrival_times3 = []
    interarrival_times4 = []
    packet_sizes = []
    spike_start = 0
    spike_end = 2

    # Spike 1 (around 1 second)
    spike1_start = 0
    spike1_end = 2
    spike1_packets = int(num_packets * 0.3)
    interarrival_times1.extend(np.random.uniform(spike_start, spike_end, spike1_packets))
    packet_sizes.extend(np.random.randint(1, 20, spike1_packets))

    # Spike 2 (around 7 seconds)
    spike2_start = 0
    spike2_end = 2
    spike2_packets = int(num_packets * 0.3)
    interarrival_times.extend(np.random.uniform(spike_start, spike_end, spike2_packets))
    packet_sizes.extend(np.random.randint(1, 20, spike2_packets))
    interarrival_times[0] += 6

    # Spike 3 (around 20 seconds)
    spike3_start = 20
    spike3_end = 22
    spike3_packets = int(num_packets * 0.3)
    interarrival_times.extend(np.random.uniform(spike_start, spike_end, spike3_packets))
    packet_sizes.extend(np.random.randint(1, 20, spike3_packets))

    # Sparse packets outside the spikes
    sparse_packets = num_packets - len(interarrival_times)
    interarrival_times.extend(np.random.uniform(0, total_time, sparse_packets))
    packet_sizes.extend(np.random.randint(1, 10, sparse_packets))

    sort_indices = np.argsort(interarrival_times)
    interarrival_times_sorted = interarrival_times[sort_indices]
    packet_sizes_sorted = packet_sizes[sort_indices]

    return interarrival_times_sorted, packet_sizes_sorted


interarrival_times = [0, 0.1, 0.12, 0.2, 0.6]
packet_sizes = [10, 10, 1, 1, 20]
time_resolution = 0.5
time_slices, bandwidth = _calc_bandwidth(interarrival_times, packet_sizes, time_resolution, verbose=True)

interarrival_times = [0, 0.1, 0.12, 0.2, 0.6]
packet_sizes = [10, 10, 1, 1, 20]
time_resolution = 0.1
time_slices, bandwidth = _calc_bandwidth(interarrival_times, packet_sizes, time_resolution, verbose=True)

interarrival_times = [0, 0.1, 0.12, 0.2, 0.6]
packet_sizes = [10, 10, 1, 1, 20]
time_resolution = 0.5
time_slices, bandwidth = _calc_bandwidth(interarrival_times, packet_sizes, time_resolution, verbose=True)


interarrival_times, packet_sizes = gen_interarrival_and_pkt_sizes()
time_slices, bandwidth = _calc_bandwidth(interarrival_times, packet_sizes, time_resolution, verbose=True)
