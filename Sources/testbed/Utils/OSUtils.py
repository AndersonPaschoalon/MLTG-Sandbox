import fcntl
import json
import os
import socket
import struct
import subprocess
import threading


class OSUtils:

    __debug_mode__ = True

    def __init__(self):
        pass

    @staticmethod 
    def check_port_open(port):
        import socket
        with socket.socket() as s:
            return s.connect_ex(('localhost', port)) == 0

    """
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
    """
    @staticmethod
    def run(command="ls", new_console=False, print_command=True, use_xterm=True):
        """
        Execute command either in current terminal or new window.
        
        Args:
            command: Command string to execute
            new_console: Whether to spawn new terminal
            print_command: Print command before execution
            use_xterm: Use xterm instead of gnome-terminal when new_console=True
        """
        if print_command:
            print(f"[CMD] {command}")

        def execute():
            try:
                if new_console:
                    if use_xterm:
                        # xterm command format: -hold keeps window open after command completes
                        subprocess.run([
                            "xterm",
                            "-geometry", "100x30",  # Window size
                            "-fg", "white",        # Text color
                            "-bg", "black",        # Background
                            "-title", "Mininet Console",
                            "-e", command
                        ], check=True)
                    else:
                        subprocess.run([
                            "gnome-terminal",
                            "--",
                            "bash",
                            "-c",
                            f"{command}; exec bash"  # Keeps terminal open
                        ], check=True)
                else:
                    subprocess.run(command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Command failed: {e}")

        # Run in thread (keep existing behavior)
        threading.Thread(target=execute, daemon=True).start()


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
