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

    #@staticmethod
    #def cmd_async(mn_host, command="ls", print_command=True):
    #    if print_command:
    #        print(command)
    #    def execute_command():
    #        mn_host.cmd(command)
    #    the_thread = Thread(target=execute_command)
    #    the_thread.start()
    #    return the_thread

    #@staticmethod
    #def cmd_join(the_thread):
    #    the_thread.join()




