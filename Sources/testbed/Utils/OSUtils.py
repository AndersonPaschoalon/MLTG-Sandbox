import os
import subprocess
import threading


class OSUtils:

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