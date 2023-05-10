import os
import numpy as np
import math
import pywt
import pandas as pd


class Utils:

    @staticmethod
    def diff(lst):
        diff_array = [lst[i] - lst[max(i - 1, 0)] for i in range(0, len(lst))]
        return diff_array

    @staticmethod
    def calc_interarrival_times(lst):
        return np.array(Utils.diff(lst))

    @staticmethod
    def calc_arrival_times(interarrival_times):
        arrival_times = np.cumsum(interarrival_times)
        return arrival_times.tolist()

    @staticmethod
    def mkdir(dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    @staticmethod
    def calc_bandwidth(interarrival_times, packet_sizes, time_resolution=1.0, verbose=False):
        total_time = np.sum(interarrival_times)
        num_slices = math.ceil(total_time / time_resolution)
        time_slices = np.arange(time_resolution, total_time + time_resolution, time_resolution)
        pkt_size_acc = np.zeros(num_slices)
        curr_slice = 0
        curr_time = 0
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

    @staticmethod
    def calc_pps(interarrival_times, time_resolution=1.0, verbose=False):
        total_time = np.sum(interarrival_times)
        num_slices = math.ceil(total_time / time_resolution)
        time_slices = np.arange(time_resolution, total_time + time_resolution, time_resolution)
        pkt_size_acc = np.zeros(num_slices)
        curr_slice = 0
        curr_time = 0
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
            pkt_size_acc[curr_slice] += 1
        # calc the bandwidth
        pps = pkt_size_acc / time_resolution
        if verbose:
            print("Time Slices:", time_slices)
            print("Packet per Second:", pps)
        return time_slices, pps

    @staticmethod
    def calc_instant_bw(inter_arrivals, packet_sizes):
        return packet_sizes[1:] / inter_arrivals[1:]

    @staticmethod
    def wavelet_multiresolution_energy_analysis_xy_from_bw(bandwidth_data, wavelet="haar"):
        num_scales = len(bandwidth_data)

        energy_values = []
        for j in range(1, num_scales + 1):
            # Perform wavelet transform
            # coeffs = pywt.wavedec(bandwidth_data[j - 1], 'db4', level=num_scales)
            coeffs = pywt.wavedec(bandwidth_data[j - 1], wavelet, level=num_scales)
            cA = coeffs[0]
            # Calculate energy
            energy = np.sum(np.square(cA))
            energy_values.append(np.log2(energy))

        scales = np.arange(1, num_scales + 1)

        return scales, energy_values

    @staticmethod
    def wavelet_multiresolution_energy_analysis_xy(arrival_times, packet_sizes, number_of_scales, wavelet='haar'):
        inter_arrival_times = Utils.calc_interarrival_times(arrival_times)

        # calc bandwidth in many reolutions
        bandwidth_data = []
        for j in range(1, number_of_scales):
            time_resolution = pow(2, j - 1)
            print(f"Calc bandwidth for time resolution of {time_resolution}ms")
            _, bandwidth = Utils.calc_bandwidth(inter_arrival_times, packet_sizes, time_resolution=time_resolution)
            bandwidth_data.append(bandwidth)

        # perform wavelet multiresolution energy analysis
        scales, energy_values = Utils.wavelet_multiresolution_energy_analysis_xy_from_bw(bandwidth_data, wavelet)

        return scales, energy_values

    # -*- coding: utf-8 -*-
    # Reference: https://en.wikipedia.org/wiki/Hurst_exponent
    # python 3.6.2 AMD64
    # 2018/4/19
    # Calculate Hurst exponent based on Rescaled range (R/S) analysis
    # How to use (example):
    # import Hurst
    # ts = list(range(50))
    # hurst = Hurst.hurst(ts)
    # Tip: ts has to be object list(n_samples,) or np.array(n_samples,)
    # https://github.com/RyanWangZf/Hurst-exponent-R-S-analysis-/tree/master
    @staticmethod
    def hurst(ts):
        ts = list(ts)
        n = len(ts)
        if n < 20:
            raise ValueError("Time series is too short! input series ought to have at least 20 samples!")

        max_k = int(np.floor(n / 2))
        r_s_dict = []
        for k in range(10, max_k + 1):
            R, S = 0, 0
            # split ts into subsets
            subset_list = [ts[i:i + k] for i in range(0, n, k)]
            if np.mod(n, k) > 0:
                subset_list.pop()
                # tail = subset_list.pop()
                # subset_list[-1].extend(tail)
            # calc mean of every subset
            mean_list = [np.mean(x) for x in subset_list]
            for i in range(len(subset_list)):
                cumsum_list = pd.Series(subset_list[i] - mean_list[i]).cumsum()
                R += max(cumsum_list) - min(cumsum_list)
                S += np.std(subset_list[i])
            r_s_dict.append({"R": R / len(subset_list), "S": S / len(subset_list), "n": k})

        log_r_s = []
        log_n = []
        array_r_s = []
        array_n = []
        print(r_s_dict)
        for i in range(len(r_s_dict)):
            r_s = (r_s_dict[i]["R"] + np.spacing(1)) / (r_s_dict[i]["S"] + np.spacing(1))
            log_r_s.append(np.log(r_s))
            log_n.append(np.log(r_s_dict[i]["n"]))
            array_r_s.append(r_s)
            array_n.append(r_s_dict[i]["n"])
        h, c = np.polyfit(log_n, log_r_s, 1)
        return h, c, array_r_s, array_n




