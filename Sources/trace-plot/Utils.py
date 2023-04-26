import os


class Utils:

    @staticmethod
    def diff(lst):
        diff_array = [lst[i] - lst[max(i - 1, 0)] for i in range(0, len(lst))]
        return diff_array

    @staticmethod
    def mkdir(dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)