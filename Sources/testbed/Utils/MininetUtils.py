import subprocess
import threading


class MininetUtils:

    def __init__(self):
        pass

    @staticmethod
    def host_ip(host):
        try:
            ip_addr = h1.cmd('ifconfig | grep "inet " | awk \'{print $2}\'')
            return ip_addr
        except:
            return ""



