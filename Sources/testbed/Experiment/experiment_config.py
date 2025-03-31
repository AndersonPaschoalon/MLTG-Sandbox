import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExperimentConfig:
    """Immutable configuration container for experiment parameters"""
    name: str
    pcap: str
    out_dir: str
    client_capture_if: str
    server_capture_if: str
    display_mininet_cli: bool
    tcpdump_start_delay: int
    tcpdump_stop_delay: int
    verbose: bool
    log_file: str
    network_loss: float
    network_delay: str
    run_capture: bool
    run_qa: bool
    qa_duration: int
    qa_interval: int
    experiment_type: str

    @classmethod
    def from_xml_element(cls, elem: ET.Element) -> 'ExperimentConfig':
        """Factory method to create config from XML element with null checks"""
        def get_text(field: str, default: Optional[str] = None) -> str:
            if (node := elem.find(field)) is not None and node.text is not None:
                return node.text.strip()
            if default is not None:
                return default
            raise ValueError(f"Missing required field: {field}")

        def get_bool(field: str, default: bool = False) -> bool:
            return get_text(field, str(default)).lower() == "true"

        def get_int(field: str, default: int = 0) -> int:
            return int(get_text(field, str(default)))

        def get_float(field: str, default: float = 0.0) -> float:
            return float(get_text(field, str(default)))

        return cls(
            name=get_text("name"),
            pcap=get_text("pcap"),
            out_dir=get_text("out_dir", "results"),  # Default folder
            client_capture_if=get_text("client_capture_if", "h1-eth0"),
            server_capture_if=get_text("server_capture_if", "h2-eth0"),
            display_mininet_cli=get_bool("display_mininet_cli", False),
            tcpdump_start_delay=get_int("tcpdump_start_delay", 2),
            tcpdump_stop_delay=get_int("tcpdump_stop_delay", 10),
            verbose=get_bool("verbose", False),
            log_file=get_text("log_file", "experiment.log"),
            network_loss=get_float("network_loss", 0.0),
            network_delay=get_text("network_delay", "0ms"),
            run_capture=get_bool("run_capture", True),
            run_qa=get_bool("run_qa", False),
            qa_duration=get_int("qa_duration", 60),
            qa_interval=get_int("qa_interval", 1),
            experiment_type=elem.get("type", "simple-topo")  # Default topology
        )