import os


class Utils:

    @staticmethod
    def diff(lst):
        return [lst[i] - lst[i - 1] for i in range(1, len(lst))]

    @staticmethod
    def mkdir(dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)