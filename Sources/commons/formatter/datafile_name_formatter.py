import os
import re
from typing import List


class DatafileNameFormatter:

    def __init__(self, out_dir: str, experiment_name: str, experiment_test: str):
        """
        Initialize formatter for experiment test.
        Automatically creates the directory structure.
        """
        self.experiment_name = experiment_name
        self.experiment_test = experiment_test
        self.out_dir = out_dir

        # Create base directory
        self.base_dir = os.path.join(self.out_dir, experiment_name, experiment_test)
        os.makedirs(self.base_dir, exist_ok=True)

    def experiment_dir(self):
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
        Generate a complete file path with all components.
        Format: {file_identifier}.{tool}.{host}.{type}.{meta}
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
        Generate a complete file path with all components.
        Format: {file_identifier}.{tool}.{host}.{type}.{meta}.{ext}
        """
        filename = ".".join(
            [
                file_identifier,
                tool_under_test,
                host_name,
                host_type,
                file_metadata,
                file_extension,
            ]
        )
        return os.path.join(self.base_dir, filename)

    def list_names(
        self,
        file_identifier: str,
        file_extension: str,
        host_type: str = "",
        tool_under_test: str = "",
    ) -> List[str]:
        """
        List existing files matching criteria.
        Returns full paths to matching files.
        """
        # Build regex pattern with fixed 5 components before extension
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

    def parse(self, file_name: str, metadata: str = "tool_under_test") -> str:
        """
        Extract specific component from filename.
        Components always in order:
        [file_id, tool, host, type, meta, ext]
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
            return parts[component_map[metadata]]
        except KeyError:
            raise ValueError(f"Invalid metadata field: {metadata}")


if __name__ == "__main__":
    fmt = DatafileNameFormatter("Results", "Banana", "pcap")
    file_name = fmt.mknameext("capture", "iperf", "h1", "client", "pcap")
    print(f"file_name:{file_name}")
    list_of_names = fmt.list_names("pcap")
    print(f"list_of_names:{list_of_names}")
    for n in list_of_names:
        print(f"tool_under_test:{fmt.parse(n, 'tool_under_test')}")
        print(f"file_metadata:{fmt.parse(n, 'file_metadata')}")
        print(f"host_name:{fmt.parse(n, 'host_name')}")
        print(f"host_type:{fmt.parse(n, 'host_type')}")
