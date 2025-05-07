import os
import re
from typing import List


class RawDataNameFormatter:
    """
    A utility class for generating and managing standardized filenames for experiment data.

    This class helps create a consistent file naming convention, ensures the directory structure
    exists, and provides utilities to list and parse filenames.

    Filename format (with extension):
        {file_identifier}.{tool_under_test}.{host_name}.{host_type}.{file_metadata}.{file_extension}
    """

    def __init__(self, out_dir: str, experiment_name: str, experiment_test: str):
        """
        Initialize the formatter with output directory and experiment identifiers.

        Args:
            out_dir (str): Root directory for output files.
            experiment_name (str): Name of the experiment.
            experiment_test (str): Specific test within the experiment.

        Creates the directory structure:
            {out_dir}/{experiment_name}/{experiment_test}
        """
        self.experiment_name = experiment_name
        self.experiment_test = experiment_test
        self.out_dir = out_dir

        # Create base directory
        self.base_dir = os.path.join(self.out_dir, experiment_name, experiment_test)
        os.makedirs(self.base_dir, exist_ok=True)

    def experiment_dir(self) -> str:
        """
        Return the path to the top-level experiment directory.

        Returns:
            str: Path to {out_dir}/{experiment_name}
        """
        return os.path.join(self.out_dir, self.experiment_name)

    def mkname(
        self,
        file_identifier: str,
        tool_under_test: str,
        host_name: str,
        host_type: str,
        file_metadata: str = "0",
    ) -> str:
        """
        Generate a standardized filename (without extension) for an experiment result.

        Args:
            file_identifier (str): Logical identifier for the file (e.g., "capture").
            tool_under_test (str): Name of the tool generating the file (e.g., "iperf").
            host_name (str): Name of the host (e.g., "h1").
            host_type (str): Type of host (e.g., "client", "server").
            file_metadata (str): Optional metadata (default is "0").

        Returns:
            str: Full file path with generated name.
        """
        filename = ".".join(
            [
                file_identifier,
                tool_under_test,
                host_name,
                host_type,
                file_metadata,
            ]
        )
        return os.path.join(self.base_dir, filename)

    def mknameext(
        self,
        file_identifier: str,
        tool_under_test: str,
        host_name: str,
        host_type: str,
        file_extension: str,
        file_metadata: str = "0",
    ) -> str:
        """
        Generate a standardized filename with an extension for experiment output.

        Args:
            file_identifier (str): Logical identifier for the file (e.g., "capture").
            tool_under_test (str): Name of the tool generating the file (e.g., "iperf").
            host_name (str): Name of the host (e.g., "h1").
            host_type (str): Type of host (e.g., "client", "server").
            file_extension (str): File extension (e.g., "pcap", "csv").
            file_metadata (str): Optional metadata (default is "0").

        Returns:
            str: Full file path with generated name including extension.
        """
        base_name = self.mkname(
            file_identifier=file_identifier,
            tool_under_test=tool_under_test,
            host_name=host_name,
            host_type=host_type,
            file_metadata=file_metadata,
        )
        return f"{base_name}.{file_extension}"

    def list_names(
        self,
        file_identifier: str,
        file_extension: str,
        host_type: str = "",
        tool_under_test: str = "",
    ) -> List[str]:
        """
        List filenames in the experiment directory matching a given pattern.

        Args:
            file_identifier (str): Logical identifier for the file (required).
            file_extension (str): File extension to match (e.g., "pcap").
            host_type (str): Optional host type filter.
            tool_under_test (str): Optional tool name filter.

        Returns:
            List[str]: List of full file paths that match the pattern.
        """
        pattern_parts = [
            re.escape(file_identifier),
            re.escape(tool_under_test) if tool_under_test else r"[^\.]+",
            r"[^\.]+",  # host_name (any value)
            re.escape(host_type) if host_type else r"[^\.]+",
            r"[^\.]+",  # metadata (always present, could be "0")
            re.escape(file_extension),
        ]
        pattern = "^" + "\.".join(pattern_parts) + "$"

        return [
            os.path.join(self.base_dir, f)
            for f in os.listdir(self.base_dir)
            if re.fullmatch(pattern, f)
        ]

    def parse(self, file_name: str, field_key: str = "tool_under_test") -> str:
        """
        Extract a specific component from a filename based on field key.

        Args:
            file_name (str): Full or relative path to the file.
            field_key (str): One of ["file_identifier", "tool_under_test", "host_name",
                                    "host_type", "file_metadata"]

        Returns:
            str: The extracted value corresponding to the field key.

        Raises:
            ValueError: If the filename is not in the expected format or field key is invalid.
        """
        parts = os.path.basename(file_name).split(".")
        if len(parts) != 6:
            raise ValueError(f"Invalid filename format: {file_name}")

        component_map = {
            "file_identifier": 0,
            "tool_under_test": 1,
            "host_name": 2,
            "host_type": 3,
            "file_metadata": 4,
        }

        try:
            return parts[component_map[field_key]]
        except KeyError:
            raise ValueError(f"Invalid field key: {field_key}")


if __name__ == "__main__":
    fmt = RawDataNameFormatter("Results", "Banana", "pcap")
    file_name = fmt.mknameext("capture", "iperf", "h1", "client", "pcap")
    print(f"file_name:{file_name}")
    list_of_names = fmt.list_names("pcap")
    print(f"list_of_names:{list_of_names}")
    for n in list_of_names:
        print(f"tool_under_test:{fmt.parse(n, 'tool_under_test')}")
        print(f"file_metadata:{fmt.parse(n, 'file_metadata')}")
        print(f"host_name:{fmt.parse(n, 'host_name')}")
        print(f"host_type:{fmt.parse(n, 'host_type')}")
