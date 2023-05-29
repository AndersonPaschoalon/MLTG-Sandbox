import os
import subprocess
import threading
import socket
import fcntl
import struct
import json


class OSUtils:

    __debug_mode__ = True

    def __init__(self):
        pass

    @staticmethod
    def run(command="ls", new_console=False, print_command=True):
        if print_command:
            print(command)
        def execute_command():
            if new_console:
                subprocess.run(["gnome-terminal", "--", "bash", "-c", command])
            else:
                subprocess.run(command, shell=True)

        thread = threading.Thread(target=execute_command)
        thread.start()

    @staticmethod
    def create_directory(directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created.")
        else:
            print(f"Directory '{directory_path}' already exists.")
        return

    @staticmethod
    def breakpoint(msg=""):
        if OSUtils.__debug_mode__:
            print("***************************************************")
            print(str(msg))
            input("Press any key to continue...")
