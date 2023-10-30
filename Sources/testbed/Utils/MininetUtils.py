import subprocess
import threading


class MininetUtils:

    def __init__(self):
        pass

    @staticmethod
    def host_ip(host, interface):
        command = f"ip -o -4 addr show dev {interface} | awk '{{split($4,a,\"/\"); print a[1]}}'"
        print(f"host$ <{command}>")
        ip_addr = host.cmd(command).strip()
        return ip_addr





