import os
import re
from typing import List

from commons.pylang.repr_mixin import ReprMixin


class RawDataNameFormatter(ReprMixin):
    """
    A utility class for generating and managing standardized filenames for experiment data.

    This class helps create a consistent file naming convention, ensures the directory structure
    exists, and provides utilities to list and parse filenames.

    Filename format (with extension):
        {file_identifier}.{tool_under_test}.{host_name}.{host_type}.{file_metadata}.{file_extension}
    """

    FILE_IDENTIFIER = "file_identifier"
    TEST_TARGET = "test_target"
    HOST_NAME = "host_name"
    HOST_TYPE = "host_type"
    FILE_METADATA = "file_metadata"
    FILE_EXTENSION = "file_extension"

    def __init__(self, out_dir: str, experiment_name: str, experiment_test: str):
        """
        A utility class for generating and managing standardized filenames for experiment data.
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

    @staticmethod
    def parse(file_name: str, field_key: str = "test_target") -> str:
        """
        Extract a specific component from a filename based on field key.

        Components:
            - experiment_name: name of the experiment run.
            - file_identifier: identifier for the file (e.g., "capture")
            - test_target: tool under test (Eg.: iperf) or ground-truth(pcap file name)
            - host_name: name of the host (e.g., "h1")
            - host_type: type of host (e.g., "client", "server")
            - file_metadata: optional metadata (default is "0")
            - file_extension: file extension (e.g., "pcap", "csv")
        The filename format is:
            {file_identifier}.{test_target}.{host_name}.{host_type}.{file_metadata}.{file_extension}
        or
            {experiment_name}.{file_identifier}.{test_target}.{host_name}.{host_type}.{file_metadata}.{file_extension}
        or
            {experiment_name}.{test_target}.{file_extension}
        where the first format is used for raw data captured from experiments and second format
        is used used for ground-truth data.

        Args:
            file_name (str): Full or relative path to the file.
            field_key (str): One of [
                "experiment_name"
                "file_identifier",
                "test_target",
                "host_name",
                "host_type",
                "file_metadata",
                "file_extension"
            ].

        Returns:
            str: The extracted value corresponding to the field key.

        Raises:
            ValueError: If the filename is not in the expected format or field key is invalid.
        """
        print(f"=====>>> {file_name}")
        parts = os.path.basename(file_name).split(".")
        print(len(parts))
        if len(parts) != 7 and len(parts) != 6 and len(parts) != 3:
            raise ValueError(f"Invalid filename format: {file_name}")

        if len(parts) == 7:
            component_map = {
                "experiment_name": 0,
                "file_identifier": 1,
                "test_target": 2,
                "host_name": 3,
                "host_type": 4,
                "file_metadata": 5,
                "file_extension": 6,
            }
            try:
                return parts[component_map[field_key]]
            except KeyError:
                raise ValueError(f"Invalid field key: {field_key}")
        elif len == 6:
            component_map = {
                "file_identifier": 0,
                "test_target": 1,
                "host_name": 2,
                "host_type": 3,
                "file_metadata": 4,
                "file_extension": 5,
            }

            try:
                return parts[component_map[field_key]]
            except KeyError:
                raise ValueError(f"Invalid field key: {field_key}")
        else:  # len == 3
            component_map = {
                "file_identifier": 0,
                "test_target": 1,
                "file_extension": 2,
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
