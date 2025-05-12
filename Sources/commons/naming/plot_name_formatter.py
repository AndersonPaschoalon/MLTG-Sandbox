import os
from typing import List

from commons.pylang.repr_mixin import ReprMixin


class PlotNameFormatter(ReprMixin):
    """
    Formatter for naming and storing plot files related to experiment results.

    Plot files are stored in:
        <out_dir>/<experiment_name>/plot/

    Naming convention:
        <plot_name>.m1-m2-...mn.<extension>

    Where:
        - plot_name: Type of metric being plotted (e.g., bandwidth, packet_per_second)
        - m1-m2-...mn: Dash-separated names of the compared elements
        - extension: Plot file extension (default: 'png')
    """

    # Plot type constants
    BANDWIDTH = "bandwidth"
    PACKET_PER_SECOND = "packet_per_second"
    FLOW_PER_SECOND = "flow_per_second"

    def __init__(self, out_dir: str, experiment_name: str):
        """
        Initialize the plot formatter for a given experiment.

        Args:
            out_dir (str): Base output directory.
            experiment_name (str): Name of the experiment.
        """
        self.experiment_name = experiment_name
        self.out_dir = out_dir
        self.plot_dir = os.path.join(out_dir, experiment_name, "plot")
        os.makedirs(self.plot_dir, exist_ok=True)

    def mknameext(
        self, plot_name: str, compared_elements: List[str], extension: str = "png"
    ) -> str:
        """
        Generate the full path for a plot file.

        Args:
            plot_name (str): Type of metric/plot (e.g., 'bandwidth').
            compared_elements (List[str]): Elements being compared (e.g., ['iperf', 'tcpreplay']).
            extension (str): File extension (default: 'png').

        Returns:
            str: Full path to the plot file.
        """
        element_part = "-".join(compared_elements)
        filename = f"{plot_name}.{element_part}.{extension}"
        return os.path.join(self.plot_dir, filename)


if __name__ == "__main__":
    fmt = PlotNameFormatter("Results", "Banana")
    path = fmt.mknameext(fmt.BANDWIDTH, ["iperf", "tcpreplay"])
    print("Plot path:", path)
