import os
import subprocess
import threading

class Utils:

    @staticmethod
    def run(command="ls", new_console=False):
        def execute_command():
            if new_console:
                subprocess.run(["gnome-terminal", "--", "bash", "-c", command])
            else:
                subprocess.run(command, shell=True)

        thread = threading.Thread(target=execute_command)
        thread.start()
