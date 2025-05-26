import os
import re
from typing import List

from commons.pylang.repr_mixin import ReprMixin


class AnalysisDataNameFormatter(ReprMixin):
    """
    Formatter for generating and parsing filenames for analysis-stage data.

    This class centralizes all logic related to naming and locating analysis files,
    which are derived from raw experimental data and saved in a unified directory.

    Directory structure:
        <out_dir>/<experiment_name>/analysis/

    Filename structure:
        <performed_analysis>.<test_target>.<extension>

    Example:
        bw_pps_fps.iperf.csv
    """

    # Analysis identifiers (add more as needed)
    BW_PPS_FPS = "bw_pps_fps"
    INTERARRIVAL = "inter_arrival_ttl"
    BURST_SIZES = "burst_sizes"
    BURST_DURATIONS = "burst_durations"
    BURST_INTERVALS = "burst_intervals"
    WAVELET = "wavelet"

    def __init__(self, out_dir: str, experiment_name: str):
        """
        Formatter for generating and parsing filenames for analysis-stage data.
        Initialize the formatter for a specific experiment's analysis data.

        Args:
            out_dir (str): Root output directory for all results.
            experiment_name (str): The name of the experiment.
        """
        self.experiment_name = experiment_name
        self.out_dir = out_dir
        self.analysis_dir = os.path.join(out_dir, experiment_name, "analysis")
        os.makedirs(self.analysis_dir, exist_ok=True)

    def mknameext(
        self, performed_analysis: str, test_target: str, extension: str = "csv"
    ) -> str:
        """
        Generate full path for an analysis data file.

        Args:
            performed_analysis (str): The type of analysis performed (e.g., 'bw_pps_fps').
            test_target (str): The source or tool this data represents (e.g., 'iperf').
            extension (str): File extension (default is 'csv').

        Returns:
            str: Full path to the analysis file.
        """
        filename = f"{performed_analysis}.{test_target}.{extension}"
        return os.path.join(self.analysis_dir, filename)

    def list_names(
        self, performed_analysis: str = "", extension: str = "csv"
    ) -> List[str]:
        """
        List existing analysis files matching criteria.

        Args:
            performed_analysis (str): Filter by analysis type. If empty, matches all.
            extension (str): File extension to filter (default 'csv').

        Returns:
            List[str]: List of full paths to matching analysis files.
        """
        pattern_parts = [
            re.escape(performed_analysis) if performed_analysis else r"[^\.]+",
            r"[^\.]+",  # test_target
            re.escape(extension),
        ]
        pattern = "^" + "\.".join(pattern_parts) + "$"

        return [
            os.path.join(self.analysis_dir, f)
            for f in os.listdir(self.analysis_dir)
            if re.fullmatch(pattern, f)
        ]

    @staticmethod
    def parse(file_name: str, field_key: str = "performed_analysis") -> str:
        """
        Extract a component from the analysis filename.

        Components:
            - performed_analysis
            - test_target (tool under test or ground-truth)

        Args:
            file_name (str): Full or relative filename.
            field_key (str): One of ['performed_analysis', 'test_target'].

        Returns:
            str: Value of the requested component.

        Raises:
            ValueError: If file format or field_key is invalid.
        """
        parts = os.path.basename(file_name).split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid analysis filename format: {file_name}")

        component_map = {
            "performed_analysis": 0,
            "test_target": 1,
        }

        try:
            return parts[component_map[field_key]]
        except KeyError:
            raise ValueError(f"Invalid field key: {field_key}")


if __name__ == "__main__":
    fmt = AnalysisDataNameFormatter("Results", "Banana")
    file = fmt.mknameext(fmt.BW_PPS_FPS, "iperf")
    print("Analysis File:", file)

    files = fmt.list_names(performed_analysis=fmt.BW_PPS_FPS)
    for f in files:
        print(f"→ Target: {fmt.parse(f, 'test_target')}")
