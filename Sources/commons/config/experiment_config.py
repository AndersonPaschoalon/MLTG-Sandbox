import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExperimentConfig:
    """Immutable configuration container for experiment parameters"""

    name: str
    pcap: str
    out_dir: str
    display_mininet_cli: bool
    verbose: bool
    network_loss: float
    network_delay: str
    run_capture: bool
    run_qa: bool
    qa_duration: int
    qa_interval: int
    experiment_type: str

    def experiment_dir(self):
        return os.path.join(self.out_dir, self.name)
    
    def experiment_db_dir(self):
        return os.path.join(self.experiment_dir(), "db")

    @staticmethod
    def get_by_name(file: str, name: str) -> "ExperimentConfig":
        list_config = ExperimentConfig.load(file)
        for config in list_config:
            if config.name == name:
                return config
        raise ValueError(
            f"Could not find experiment name {name} on xml file {file}. Please  check the name and file again."
        )

    @staticmethod
    def load(file: str) -> List["ExperimentConfig"]:
        if not os.path.exists(file):
            raise FileNotFoundError(file)
        try:
            tree = ET.parse(file)
            return [
                ExperimentConfig._from_xml_element(elem)
                for elem in tree.findall("experiment")
            ]
        except Exception as e:
            raise ValueError(f"Error parsing XML: {e}") from e

    @classmethod
    def _from_xml_element(cls, elem: ET.Element) -> "ExperimentConfig":
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
            display_mininet_cli=get_bool("display_mininet_cli", False),
            verbose=get_bool("verbose", False),
            network_loss=get_float("network_loss", 0.0),
            network_delay=get_text("network_delay", "0ms"),
            run_capture=get_bool("run_capture", True),
            run_qa=get_bool("run_qa", False),
            qa_duration=get_int("qa_duration", 60),
            qa_interval=get_int("qa_interval", 1),
            experiment_type=elem.get("type", "simple-topo"),  # Default topology
        )
