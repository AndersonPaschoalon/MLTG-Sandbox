import os
import socket
import subprocess
import sys
import threading
from contextlib import contextmanager
from typing import IO, Generator, List, Optional, Tuple


class OSUtils:
    """Operating system utility methods for debugging and process execution."""

    @staticmethod
    def write_on_file(string: str, filename: str) -> bool:
        """
        Writes the provided string to a file with the given filename.

        Parameters:
        -----------
        string : str
            The content to be written to the file.
        filename : str
            The name of the file where the content will be written.

        Returns:
        --------
        None
            The method does not return any value. It prints a success or error message to the console.

        Example:
        --------
        >>> PyLang.write_on_file("Hello, world!", "example.txt")
        Content successfully written to example.txt
        """
        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(string)
            print(f"Content successfully written to {filename}")
            return True
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")
        return False

    @staticmethod
    def check_port_open(port: int) -> bool:
        """
        Check if a local port is available for binding.

        Args:
            port: TCP port number to check (0-65535)

        Returns:
            bool: True if port is open (not in use), False otherwise

        Example:
            >>> OSUtils.check_port_open(8080)
            False  # If port 8080 is in use
            >>> OSUtils.check_port_open(9999)
            True   # If port 9999 is available

        Note:
            Uses a quick socket connection test (TCP level)
            May return False if port is blocked by firewall
        """
        with socket.socket() as s:
            return s.connect_ex(("localhost", port)) == 0

    @staticmethod
    def ensure_clean_directory(directory_path: str) -> str:
        """
        Ensure a clean directory exists by versioning existing directories.

        Args:
            directory_path: Desired directory path (absolute or relative)

        Returns:
            str: Path to the clean directory (may be versioned if original existed)

        Example:
            >>> OSUtils.ensure_clean_directory("results")
            'results'  # Created new directory

            >>> # If 'results' exists:
            'results'  # Original moved to 'results.1' and new empty 'results' created

        Bug Warning:
            - Race condition: Directory could be created by another process
              between existence check and creation
            - No permission checking before operations
            - Symbolic links may cause unexpected behavior
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            return directory_path

        # If directory exists, find the next available version
        version = 1
        while True:
            new_path = f"{directory_path}.{version}"
            if not os.path.exists(new_path):
                os.rename(directory_path, new_path)
                os.makedirs(directory_path)
                return directory_path
            version += 1

    @staticmethod
    def breakpoint(msg=""):
        """
        Pause program execution and display a message until user continues.

        Args:
            msg: Optional message to display before pausing

        Example:
            >>> OSUtils.breakpoint("Check network configuration now")
            Check network configuration now
            Press any key to continue...

        Warning:
            - Not suitable for production environments
            - Will block indefinitely if no user input available
            - Doesn't work in non-interactive environments (e.g., cron jobs)
        """
        print(str(msg))
        input("Press any key to continue...")

    @staticmethod
    @contextmanager
    def change_directory(destination: str) -> Generator[None, None, None]:
        """Context manager for safely changing directories."""
        original_dir = os.getcwd()
        try:
            os.chdir(destination)
            yield
        finally:
            os.chdir(original_dir)

    @staticmethod
    def execute_command_at(
        cmd: list[str],
        out_dir: str,
        print_output: bool = True,
        timeout: Optional[float] = None,
    ) -> tuple[str, str]:
        """
        Execute a command safely with real-time output and deadlock prevention.

        Args:
            cmd: Command and arguments as list of strings
            out_dir: Working directory for command execution
            print_output: Whether to stream output to console
            timeout: Maximum execution time in seconds (None for no timeout)

        Returns:
            tuple: (stdout_content, stderr_content) as strings

        Raises:
            RuntimeError: If command fails or times out
            TimeoutExpired: If command exceeds timeout duration

        Example:
            >>> out, err = OSUtils.execute_command_at(["ls", "-l"], "/tmp")
            >>> print(f"Got {len(out)} bytes of output")
        """

        def _process_stream(
            stream: IO[str], output_list: list[str], is_stderr: bool = False
        ):
            """Helper to process a single output stream"""
            for line in iter(stream.readline, ""):
                output_list.append(line)
                if print_output:
                    print(line, end="", file=sys.stderr if is_stderr else sys.stdout)

        with OSUtils.change_directory(out_dir):
            try:
                print(f"{out_dir}$ {' '.join(cmd)}")
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffering
                    universal_newlines=True,
                )

                stdout_lines: list[str] = []
                stderr_lines: list[str] = []

                # Use threads to prevent deadlocks
                stdout_thread = threading.Thread(
                    target=_process_stream, args=(process.stdout, stdout_lines)
                )
                stderr_thread = threading.Thread(
                    target=_process_stream, args=(process.stderr, stderr_lines, True)
                )

                stdout_thread.start()
                stderr_thread.start()

                # Wait with timeout if specified
                process.wait(timeout=timeout)

                # Ensure threads finish
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)

                if process.returncode != 0:
                    raise subprocess.CalledProcessError(
                        process.returncode,
                        cmd,
                        "".join(stdout_lines),
                        "".join(stderr_lines),
                    )

                return "".join(stdout_lines), "".join(stderr_lines)

            except subprocess.TimeoutExpired:
                process.kill()
                raise RuntimeError(
                    f"Command timed out after {timeout} seconds"
                ) from None
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"Command failed (code {e.returncode}): {e.stderr}"
                ) from e
            except Exception as e:
                raise RuntimeError(f"Unexpected error: {str(e)}") from e

    @staticmethod
    def execute_on_shell(
        command: str,
        new_console: bool = False,
        print_command: bool = True,
        use_xterm: bool = True,
    ) -> None:
        """
        Execute a shell command either in current terminal or new window.

        Args:
            command: Shell command string to execute
            new_console: Launch in new terminal window when True
            print_command: Print the command before execution
            use_xterm: Use xterm instead of gnome-terminal when new_console=True

        Returns:
            None: Runs command asynchronously in a daemon thread

        Example:
            >>> # Run simple command in current terminal
            >>> OSUtils.run("ping -c 4 google.com")
            [CMD] ping -c 4 google.com
            PING google.com (142.250.217.78) 56(84) bytes of data...

            >>> # Run in new xterm window
            >>> OSUtils.run("top", new_console=True)
            [CMD] top  # Opens new xterm window running top

        Warning:
            - Shell injection risk when using shell=True (for non-new_console)
            - Daemon thread may terminate abruptly if main program exits
            - Windows compatibility not implemented (xterm/gnome-terminal specific)
        """

        if print_command:
            print(f"[CMD] {command}")

        def execute():
            try:
                if new_console:
                    if use_xterm:
                        # xterm command format: -hold keeps window open after command completes
                        subprocess.run(
                            [
                                "xterm",
                                "-geometry",
                                "100x30",  # Window size
                                "-fg",
                                "white",  # Text color
                                "-bg",
                                "black",  # Background
                                "-title",
                                "Mininet Console",
                                "-e",
                                command,
                            ],
                            check=True,
                        )
                    else:
                        subprocess.run(
                            [
                                "gnome-terminal",
                                "--",
                                "bash",
                                "-c",
                                f"{command}; exec bash",  # Keeps terminal open
                            ],
                            check=True,
                        )
                else:
                    subprocess.run(command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Command failed: {e}")

        # Run in thread (keep existing behavior)
        threading.Thread(target=execute, daemon=True).start()

    @staticmethod
    def execute_command(
        command: str, cwd: Optional[str] = None, timeout: Optional[float] = None
    ) -> Tuple[str, str, int]:
        """
        Execute a command and return its output and status code.

        Args:
            command: Command to execute as list of arguments
            cwd: Working directory (None for current directory)
            timeout: Maximum execution time in seconds (None for no timeout)

        Returns:
            tuple: (stdout, stderr, return_code)
            - stdout: Standard output as string
            - stderr: Standard error as string
            - return_code: Integer exit status (0 typically means success)

        Example:
            >>> output, errors, code = OSUtils.run_command(["ls", "-l"])
            >>> if code == 0:
            ...     print(f"Success! Output:\n{output}")
            ... else:
            ...     print(f"Failed (code {code}):\n{errors}")

        Warning:
            - Will raise subprocess.TimeoutExpired if timeout is exceeded
            - Avoid shell=True to prevent command injection
            - Large outputs may consume significant memory
        """
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                check=False,
                shell=True,
            )
            return (result.stdout, result.stderr, result.returncode)
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"Command timed out after {timeout} seconds") from e
